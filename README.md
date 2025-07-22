KuangEdit
=========

> ⚠️ **AI-GENERATED CODE** - This application was created using AI assistance (Claude AI) and may require testing and validation before production use.

A small GUI application for managing Laravel JSON translation files with advanced features for efficient translation workflow.

## 🚀 Features

### Core Functionality
- **Multi-language support** - Manage multiple JSON translation files simultaneously
- **Real-time search** - Filter translations by keys and/or values with instant results
- **Inline editing** - Edit translations directly with multi-line text support
- **Auto-save** - Optional automatic saving after each change

### Enhanced User Experience
- **Keyboard shortcuts** - Full keyboard navigation and editing support
- **Visual indicators** - Color-coded rows showing translation completeness
- **Status bar** - Real-time statistics about languages and translation keys
- **Smart filtering** - Search across keys and values with flexible options

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save all files |
| `Ctrl+F` | Focus search field |
| `Ctrl+N` | Add new translation key |
| `Ctrl+A` | Select all text (in any input field) |
| `Enter` | Edit selected translation |
| `Delete` | Delete selected translation |
| `Escape` | Clear search / Close dialogs |
| `F5` | Reload files from disk |

## 📋 Requirements

- Python 3.8+
- tkinter (usually included with Python)
- JSON translation files in Laravel format

## 🛠️ Installation & Usage

### For Laravel Projects

1. **Copy the script** to your Laravel `lang` directory:
   ```bash
   # Navigate to your Laravel project
   cd your-laravel-project/lang
   
   # Copy the main.py file here
   cp /path/to/main.py .
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

The application will automatically detect and load all `*.json` files in the current directory.

### Standalone Usage

1. Place `main.py` in any directory containing JSON translation files
2. Run: `python main.py`

## 📁 File Structure

The application expects JSON files in Laravel's translation format:

```
lang/
├── en.json          # English translations
├── es.json          # Spanish translations
├── fr.json          # French translations
└── main.py          # This application
```

### JSON File Format
```json
{
    "welcome": "Welcome to our application",
    "goodbye": "Goodbye",
    "user.name": "User Name",
    "user.email": "Email Address"
}
```

## 🎨 Visual Indicators

- 🟢 **Green rows**: All translations complete
- 🔴 **Red rows**: Missing all translations
- ⚪ **White rows**: Partially translated

## 📝 Notes

- This application modifies JSON files directly
- Always backup your translation files before use
- The app sorts keys alphabetically when saving
- Empty translation values are automatically removed from saved files

## 🤝 Contributing

Since this is AI-generated code, please:
1. Test thoroughly before production use
2. Report any bugs or issues
3. Suggest improvements or additional features
4. Validate the code meets your security requirements

## 📄 License

This project is provided as-is under the MIT License. Please review and test the code before using in production environments.