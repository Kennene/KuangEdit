import re
import os
import glob
import json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import font

"""
TranslatorApp: Enhanced GUI application for managing JSON-based Laravel translation files.
Author: Krzysztof Pacyna & ChatGPT (Enhanced by Claude)
Python Version: 3.8+
Date: 2024-10-29 (Enhanced: 2025)

Features:
- Search functionality with real-time filtering
- Keyboard shortcuts (Ctrl+S, Ctrl+F, Ctrl+N, Ctrl+D, Enter, Escape)
- Improved text editing with multi-line support
- Auto-save functionality
- Better navigation and user experience
- Status bar with statistics
- Improved error handling and validation
"""

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laravel Translator - Enhanced")
        self.root.geometry("1200x700")

        # Data storage
        self.data = {}
        self.filtered_data = {}
        self.current_search = ""
        self.auto_save = tk.BooleanVar(value=True)

        # Create menu
        self.create_menu()

        # Create main interface
        self.create_search_frame()
        self.create_table()
        self.create_buttons()
        self.create_status_bar()

        # Load files after creating UI components
        self.load_files()

        # Bind keyboard shortcuts
        self.setup_keyboard_shortcuts()

        # Initialize filtered data
        self.refresh_filtered_data()

    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save All (Ctrl+S)", command=self.save_files)
        file_menu.add_command(label="Reload Files", command=self.reload_files)
        file_menu.add_separator()
        file_menu.add_checkbutton(label="Auto-save", variable=self.auto_save)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Search (Ctrl+F)", command=self.focus_search)
        edit_menu.add_command(label="Add Key (Ctrl+N)", command=self.add_key)
        edit_menu.add_command(label="Clear Search", command=self.clear_search)

        # Language menu
        lang_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Language", menu=lang_menu)
        lang_menu.add_command(label="Add Language", command=self.add_language)
        lang_menu.add_command(label="Remove Language", command=self.remove_language)

    def create_search_frame(self):
        """Create search interface"""
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(search_frame, text="Search:", font=("Arial", 10, "bold")).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)

        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side="left", padx=(5, 10), fill="x", expand=True)

        # Add Ctrl+A support for search entry
        self.search_entry.bind("<Control-a>", self.select_all_entry)

        tk.Button(search_frame, text="Clear", command=self.clear_search).pack(side="right", padx=5)

        # Search options
        options_frame = tk.Frame(search_frame)
        options_frame.pack(side="right")

        self.search_keys = tk.BooleanVar(value=True)
        self.search_values = tk.BooleanVar(value=True)

        tk.Checkbutton(options_frame, text="Keys", variable=self.search_keys,
                      command=self.refresh_search).pack(side="left")
        tk.Checkbutton(options_frame, text="Values", variable=self.search_values,
                      command=self.refresh_search).pack(side="left")

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Global shortcuts
        self.root.bind("<Control-s>", lambda e: self.save_files())
        self.root.bind("<Control-f>", lambda e: self.focus_search())
        self.root.bind("<Control-n>", lambda e: self.add_key())
        self.root.bind("<Escape>", lambda e: self.clear_search())
        self.root.bind("<F5>", lambda e: self.reload_files())

        # Search shortcuts
        self.search_entry.bind("<Return>", lambda e: self.tree.focus())
        self.search_entry.bind("<Down>", lambda e: self.tree.focus())

        # Table shortcuts
        self.tree.bind("<Return>", self.on_enter_key)
        self.tree.bind("<Delete>", self.on_delete_key)
        self.tree.bind("<Key>", self.jump_to_key)

    def focus_search(self):
        """Focus on search entry"""
        self.search_entry.focus()
        self.search_entry.select_range(0, tk.END)

    def select_all_entry(self, event):
        """Select all text in Entry widget"""
        event.widget.select_range(0, tk.END)
        return "break"  # Prevent default behavior

    def select_all_text(self, event):
        """Select all text in Text widget"""
        event.widget.tag_add(tk.SEL, "1.0", tk.END)
        event.widget.mark_set(tk.INSERT, "1.0")
        event.widget.see(tk.INSERT)
        return "break"  # Prevent default behavior

    def clear_search(self):
        """Clear search and refresh table"""
        self.search_var.set("")
        self.search_entry.focus()

    def on_search_change(self, *args):
        """Handle search text changes"""
        self.current_search = self.search_var.get().lower()
        self.refresh_search()

    def refresh_search(self):
        """Refresh search results"""
        self.refresh_filtered_data()
        self.refresh_table()
        self.update_status()

    def refresh_filtered_data(self):
        """Filter data based on search criteria"""
        if not self.current_search:
            self.filtered_data = self.data.copy()
            return

        self.filtered_data = {}
        for lang in self.data:
            self.filtered_data[lang] = {}

        # Get all keys that match search criteria
        matching_keys = set()

        for lang, translations in self.data.items():
            for key, value in translations.items():
                key_matches = self.search_keys.get() and self.current_search in key.lower()
                value_matches = self.search_values.get() and self.current_search in str(value).lower()

                if key_matches or value_matches:
                    matching_keys.add(key)

        # Add matching keys to filtered data
        for key in matching_keys:
            for lang in self.data:
                if key in self.data[lang]:
                    self.filtered_data[lang][key] = self.data[lang][key]

    def load_files(self):
        """Load all JSON translation files from current directory"""
        self.data = {}
        json_files = glob.glob("*.json")

        if not json_files:
            messagebox.showinfo("Info", "No JSON files found in current directory.")
            # Initialize with empty data but still update headers
            self.update_table_headers()
            return

        for file_name in json_files:
            try:
                with open(file_name, "r", encoding="utf-8") as f:
                    json_text = self.clean_json(f.read())
                    self.data[file_name] = json.loads(json_text)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                self.data[file_name] = {}
                messagebox.showerror("Error", f"Failed to load file: {file_name}\nError: {str(e)}")

        self.update_table_headers()

    def reload_files(self):
        """Reload all files from disk"""
        if messagebox.askyesno("Reload Files", "This will discard any unsaved changes. Continue?"):
            self.load_files()
            self.refresh_filtered_data()
            self.refresh_table()
            self.update_status()
            messagebox.showinfo("Success", "Files reloaded successfully.")

    def clean_json(self, json_text):
        """Clean JSON text by removing trailing commas"""
        return re.sub(r",\s*([}\]])", r"\1", json_text)

    def create_table(self):
        """Create the main translation table"""
        # Create frame for table and scrollbars
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create treeview with scrollbars
        self.tree = ttk.Treeview(table_frame, show="headings", height=20)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack scrollbars and treeview
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # Configure column widths
        self.tree.bind("<Double-1>", self.on_double_click)

        # Configure tags for better visual feedback
        self.tree.tag_configure("missing", background="#ffeeee")
        self.tree.tag_configure("complete", background="#eeffee")

    def update_table_headers(self):
        """Update table column headers"""
        if not self.data:
            self.tree["columns"] = ("Key",)
        else:
            self.tree["columns"] = ("Key",) + tuple(sorted(self.data.keys()))

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.replace('.json', ''))

        # Set column widths
        self.tree.column("Key", width=200, minwidth=150)
        for lang in self.tree["columns"][1:]:
            self.tree.column(lang, width=200, minwidth=150)

    def refresh_table(self):
        """Refresh the translation table"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.filtered_data:
            return

        # Get all unique keys from filtered data
        all_keys = set()
        for lang_data in self.filtered_data.values():
            all_keys.update(lang_data.keys())

        # Sort keys naturally
        sorted_keys = sorted(all_keys, key=str.lower)

        # Add rows to table
        for key in sorted_keys:
            values = [key]
            missing_count = 0

            for lang in sorted(self.data.keys()):
                value = self.filtered_data.get(lang, {}).get(key, "")
                values.append(value)
                if not value:
                    missing_count += 1

            # Determine row tag based on completion status
            if missing_count == 0:
                tag = "complete"
            elif missing_count == len(self.data):
                tag = "missing"
            else:
                tag = ""

            self.tree.insert("", "end", values=values, tags=(tag,))

    def on_double_click(self, event):
        """Handle double-click on table row"""
        selection = self.tree.selection()
        if selection:
            item_id = selection[0]
            values = self.tree.item(item_id, "values")
            EditWindow(self, item_id, values)

    def on_enter_key(self, event):
        """Handle Enter key press in table"""
        selection = self.tree.selection()
        if selection:
            self.on_double_click(event)

    def on_delete_key(self, event):
        """Handle Delete key press in table"""
        selection = self.tree.selection()
        if selection:
            item_id = selection[0]
            key = self.tree.item(item_id, "values")[0]
            if messagebox.askyesno("Delete Key", f"Are you sure you want to delete key '{key}'?"):
                self.delete_key(key)

    def delete_key(self, key):
        """Delete a translation key"""
        for lang in self.data.keys():
            self.data[lang].pop(key, None)

        if self.auto_save.get():
            self.save_files(show_message=False)

        self.refresh_filtered_data()
        self.refresh_table()
        self.update_status()

    def update_value(self, item_id, new_key, new_values):
        """Update translation values"""
        old_key = self.tree.item(item_id, "values")[0]

        # Handle key rename
        if old_key != new_key:
            for lang in self.data.keys():
                if old_key in self.data[lang]:
                    self.data[lang][new_key] = self.data[lang].pop(old_key)

        # Update values
        lang_list = sorted(self.data.keys())
        for i, lang in enumerate(lang_list):
            if i < len(new_values):
                value = new_values[i].strip()
                if value:
                    self.data[lang][new_key] = value
                else:
                    self.data[lang].pop(new_key, None)

        if self.auto_save.get():
            self.save_files(show_message=False)

        self.refresh_filtered_data()
        self.refresh_table()
        self.update_status()

    def create_buttons(self):
        """Create action buttons"""
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Main action buttons
        tk.Button(button_frame, text="Add Language", command=self.add_language,
                 width=12).pack(side="left", padx=5)
        tk.Button(button_frame, text="Remove Language", command=self.remove_language,
                 width=12).pack(side="left", padx=5)
        tk.Button(button_frame, text="Add Key (Ctrl+N)", command=self.add_key,
                 width=15).pack(side="left", padx=5)
        tk.Button(button_frame, text="Save All (Ctrl+S)", command=self.save_files,
                 width=15, bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=5)

    def create_status_bar(self):
        """Create status bar"""
        self.status_frame = tk.Frame(self.root, relief=tk.SUNKEN, bd=1)
        self.status_frame.pack(side="bottom", fill="x")

        self.status_label = tk.Label(self.status_frame, text="Ready", anchor="w")
        self.status_label.pack(side="left", padx=5)

        self.update_status()

    def update_status(self):
        """Update status bar information"""
        if not self.data:
            self.status_label.config(text="No translation files loaded")
            return

        total_keys = len(set(key for lang in self.data.values() for key in lang.keys()))
        filtered_keys = len(set(key for lang in self.filtered_data.values() for key in lang.keys()))
        languages = len(self.data)

        if self.current_search:
            status_text = f"Languages: {languages} | Keys: {filtered_keys}/{total_keys} (filtered) | Search: '{self.current_search}'"
        else:
            status_text = f"Languages: {languages} | Keys: {total_keys}"

        self.status_label.config(text=status_text)

    def add_key(self):
        """Add new translation key"""
        AddKeyWindow(self)

    def add_language(self):
        """Add new language file"""
        dialog = LanguageDialog(self.root, "Add Language", "Enter language file name (e.g., fr.json):")
        if dialog.result:
            lang_name = dialog.result
            if not lang_name.endswith(".json"):
                lang_name += ".json"

            if lang_name in self.data:
                messagebox.showerror("Error", "Language file already exists.")
                return

            self.data[lang_name] = {}
            self.update_table_headers()
            self.refresh_filtered_data()
            self.refresh_table()
            self.update_status()

            if self.auto_save.get():
                self.save_files(show_message=False)

    def remove_language(self):
        """Remove language file"""
        if not self.data:
            messagebox.showwarning("Warning", "No languages to remove.")
            return

        dialog = LanguageSelectionDialog(self.root, "Remove Language",
                                       "Select language to remove:", list(self.data.keys()))
        if dialog.result:
            lang_name = dialog.result
            if messagebox.askyesno("Confirm", f"Are you sure you want to remove '{lang_name}'?"):
                del self.data[lang_name]
                try:
                    os.remove(lang_name)
                except FileNotFoundError:
                    pass

                self.update_table_headers()
                self.refresh_filtered_data()
                self.refresh_table()
                self.update_status()

    def save_files(self, show_message=True):
        """Save all translation files"""
        try:
            saved_files = 0
            for lang, translations in self.data.items():
                # Only save non-empty translations
                data_to_save = {key: val for key, val in translations.items() if val}

                with open(lang, "w", encoding="utf-8") as f:
                    json.dump(data_to_save, f, ensure_ascii=False, indent=4, sort_keys=True)
                saved_files += 1

            if show_message:
                messagebox.showinfo("Success", f"Successfully saved {saved_files} files.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save files: {str(e)}")

    def jump_to_key(self, event):
        """Jump to key starting with typed letter"""
        if event.char.isalnum():
            letter = event.char.lower()
            for item in self.tree.get_children():
                key = self.tree.item(item, "values")[0].lower()
                if key.startswith(letter):
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    break


class EditWindow:
    """Enhanced edit window for translation entries"""

    def __init__(self, app, item_id, values):
        self.app = app
        self.item_id = item_id
        self.values = list(values)

        self.window = tk.Toplevel(app.root)
        self.window.title(f"Edit Translation: {values[0]}")
        self.window.geometry("600x500")
        self.window.transient(app.root)

        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"+{x}+{y}")

        self.create_widgets()
        self.setup_shortcuts()

        # Set grab after window is fully created and visible
        self.window.after(10, self.window.grab_set)

        # Focus on key entry
        self.key_entry.focus()
        self.key_entry.select_range(0, tk.END)

    def create_widgets(self):
        """Create edit window widgets"""
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Key section
        key_frame = tk.LabelFrame(main_frame, text="Translation Key", font=("Arial", 10, "bold"))
        key_frame.pack(fill="x", pady=(0, 10))

        self.key_entry = tk.Entry(key_frame, font=("Arial", 11))
        self.key_entry.pack(fill="x", padx=10, pady=10)
        self.key_entry.insert(0, self.values[0])

        # Add Ctrl+A support for key entry
        self.key_entry.bind("<Control-a>", lambda e: self.app.select_all_entry(e))

        # Translations section
        trans_frame = tk.LabelFrame(main_frame, text="Translations", font=("Arial", 10, "bold"))
        trans_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Create scrollable frame for translations
        canvas = tk.Canvas(trans_frame)
        scrollbar = ttk.Scrollbar(trans_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.entries = []
        lang_list = sorted(self.app.data.keys())

        for i, lang in enumerate(lang_list):
            # Create frame for each language
            lang_frame = tk.Frame(scrollable_frame)
            lang_frame.pack(fill="x", padx=10, pady=5)

            # Language label
            lang_label = tk.Label(lang_frame, text=lang.replace('.json', ''),
                                width=15, anchor="w", font=("Arial", 10, "bold"))
            lang_label.pack(side="left")

            # Text widget for multi-line support
            text_widget = tk.Text(lang_frame, height=3, width=50, wrap=tk.WORD,
                                font=("Arial", 10))
            text_widget.pack(side="left", fill="x", expand=True, padx=(10, 0))

            # Insert current value
            current_value = self.values[i + 1] if i + 1 < len(self.values) else ""
            text_widget.insert("1.0", current_value)

            # Bind shortcuts for text widget
            text_widget.bind("<Control-Return>", self.save)
            text_widget.bind("<Escape>", lambda e: self.window.destroy())
            text_widget.bind("<Control-a>", lambda e: self.app.select_all_text(e))

            self.entries.append(text_widget)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x")

        tk.Button(button_frame, text="Save (Ctrl+S)", command=self.save,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=15).pack(side="left", padx=(0, 5))
        tk.Button(button_frame, text="Delete (Del)", command=self.delete,
                 bg="#f44336", fg="white", font=("Arial", 10), width=15).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel (Esc)", command=self.window.destroy,
                 font=("Arial", 10), width=15).pack(side="right")

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for edit window"""
        self.window.bind("<Control-s>", self.save)
        self.window.bind("<Control-Return>", self.save)
        self.window.bind("<Escape>", lambda e: self.window.destroy())
        self.window.bind("<Delete>", lambda e: self.delete())

    def save(self, event=None):
        """Save translation changes"""
        new_key = self.key_entry.get().strip()
        if not new_key:
            messagebox.showerror("Error", "Key cannot be empty.")
            return

        new_values = []
        for text_widget in self.entries:
            content = text_widget.get("1.0", tk.END).strip()
            new_values.append(content)

        self.app.update_value(self.item_id, new_key, new_values)
        self.window.destroy()

    def delete(self):
        """Delete current translation key"""
        key = self.values[0]
        if messagebox.askyesno("Delete Key", f"Are you sure you want to delete key '{key}'?"):
            self.app.delete_key(key)
            self.window.destroy()


class AddKeyWindow:
    """Window for adding new translation keys"""

    def __init__(self, app):
        self.app = app

        self.window = tk.Toplevel(app.root)
        self.window.title("Add New Translation Key")
        self.window.geometry("600x400")
        self.window.transient(app.root)

        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"+{x}+{y}")

        self.create_widgets()

        # Set grab after window is fully created
        self.window.after(10, self.window.grab_set)

        # Focus on key entry
        self.key_entry.focus()

    def create_widgets(self):
        """Create add key window widgets"""
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Key section
        key_frame = tk.LabelFrame(main_frame, text="New Translation Key", font=("Arial", 10, "bold"))
        key_frame.pack(fill="x", pady=(0, 10))

        self.key_entry = tk.Entry(key_frame, font=("Arial", 11))
        self.key_entry.pack(fill="x", padx=10, pady=10)
        self.key_entry.bind("<Return>", lambda e: self.entries[0].focus() if self.entries else None)

        # Add Ctrl+A support for key entry
        self.key_entry.bind("<Control-a>", lambda e: self.app.select_all_entry(e))

        # Translations section
        if self.app.data:
            trans_frame = tk.LabelFrame(main_frame, text="Translations", font=("Arial", 10, "bold"))
            trans_frame.pack(fill="both", expand=True, pady=(0, 10))

            self.entries = []
            for lang in sorted(self.app.data.keys()):
                lang_frame = tk.Frame(trans_frame)
                lang_frame.pack(fill="x", padx=10, pady=5)

                tk.Label(lang_frame, text=lang.replace('.json', ''),
                        width=15, anchor="w", font=("Arial", 10, "bold")).pack(side="left")

                entry = tk.Entry(lang_frame, font=("Arial", 10))
                entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
                entry.bind("<Control-Return>", self.save)
                entry.bind("<Escape>", lambda e: self.window.destroy())
                entry.bind("<Control-a>", lambda e: self.app.select_all_entry(e))

                self.entries.append(entry)
        else:
            self.entries = []
            tk.Label(main_frame, text="No languages available. Add a language first.",
                    font=("Arial", 10), fg="red").pack(pady=20)

        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x")

        tk.Button(button_frame, text="Add Key (Ctrl+S)", command=self.save,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left")
        tk.Button(button_frame, text="Cancel (Esc)", command=self.window.destroy,
                 font=("Arial", 10)).pack(side="right")

        # Bind shortcuts
        self.window.bind("<Control-s>", self.save)
        self.window.bind("<Control-Return>", self.save)
        self.window.bind("<Escape>", lambda e: self.window.destroy())

    def save(self, event=None):
        """Save new translation key"""
        new_key = self.key_entry.get().strip()
        if not new_key:
            messagebox.showerror("Error", "Key cannot be empty.")
            return

        # Check if key already exists
        for lang_data in self.app.data.values():
            if new_key in lang_data:
                messagebox.showerror("Error", f"Key '{new_key}' already exists.")
                return

        # Add new key with translations
        lang_list = sorted(self.app.data.keys())
        for i, lang in enumerate(lang_list):
            value = self.entries[i].get().strip() if i < len(self.entries) else ""
            if value:
                self.app.data[lang][new_key] = value
            else:
                self.app.data[lang][new_key] = ""

        if self.app.auto_save.get():
            self.app.save_files(show_message=False)

        self.app.refresh_filtered_data()
        self.app.refresh_table()
        self.app.update_status()
        self.window.destroy()


class LanguageDialog:
    """Simple dialog for language input"""

    def __init__(self, parent, title, prompt):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (150 // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # Create widgets
        tk.Label(self.dialog, text=prompt, font=("Arial", 10)).pack(pady=10)

        self.entry = tk.Entry(self.dialog, font=("Arial", 11), width=40)
        self.entry.pack(pady=10)
        self.entry.focus()

        # Add Ctrl+A support
        self.entry.bind("<Control-a>", self.select_all_entry)

        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="OK", command=self.ok_clicked,
                 font=("Arial", 10), width=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel_clicked,
                 font=("Arial", 10), width=10).pack(side="left", padx=5)

        # Bind keys
        self.entry.bind("<Return>", lambda e: self.ok_clicked())
        self.dialog.bind("<Escape>", lambda e: self.cancel_clicked())

        # Set grab after dialog is ready
        self.dialog.after(10, self.dialog.grab_set)

        # Wait for dialog to close
        self.dialog.wait_window()

    def ok_clicked(self):
        self.result = self.entry.get().strip()
        self.dialog.destroy()

    def select_all_entry(self, event):
        """Select all text in Entry widget"""
        event.widget.select_range(0, tk.END)
        return "break"

    def cancel_clicked(self):
        self.result = None
        self.dialog.destroy()


class LanguageSelectionDialog:
    """Dialog for selecting from existing languages"""

    def __init__(self, parent, title, prompt, options):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # Create widgets
        tk.Label(self.dialog, text=prompt, font=("Arial", 10)).pack(pady=10)

        # Listbox with scrollbar
        list_frame = tk.Frame(self.dialog)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Add options
        for option in options:
            self.listbox.insert(tk.END, option)

        # Select first item
        if options:
            self.listbox.selection_set(0)
            self.listbox.focus()

        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="OK", command=self.ok_clicked,
                 font=("Arial", 10), width=10).pack(side="left", padx=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel_clicked,
                 font=("Arial", 10), width=10).pack(side="left", padx=5)

        # Bind keys
        self.listbox.bind("<Double-1>", lambda e: self.ok_clicked())
        self.listbox.bind("<Return>", lambda e: self.ok_clicked())
        self.dialog.bind("<Escape>", lambda e: self.cancel_clicked())

        # Set grab after dialog is ready
        self.dialog.after(10, self.dialog.grab_set)

        # Wait for dialog to close
        self.dialog.wait_window()

    def ok_clicked(self):
        selection = self.listbox.curselection()
        if selection:
            self.result = self.listbox.get(selection[0])
        self.dialog.destroy()

    def cancel_clicked(self):
        self.result = None
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()
