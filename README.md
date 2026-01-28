# Caesar — Cipher Breaker

A powerful, user-friendly desktop application for breaking and analyzing classical ciphers with modern cryptanalysis tools.

![Caesar Cipher Breaker](https://img.shields.io/badge/version-3.0-blue) ![Python](https://img.shields.io/badge/python-3.8+-green) ![License](https://img.shields.io/badge/license-MIT-orange)

## Features

### Supported Ciphers

#### Substitution Ciphers (Brute Force)
- **Caesar Cipher** - All 26 shifts with automatic scoring
- **Affine Cipher** - All 312 possible key combinations

#### Instant Transforms
- **Atbash** - Letter reversal (A↔Z, B↔Y, etc.)
- **ROT47** - Extended ASCII rotation
- **ROT5** - Digit-only rotation
- **Reverse** - Simple text reversal

#### Transposition Ciphers
- **Rail Fence** - Zigzag pattern encryption
- **Columnar Transposition** - Column-based permutation

#### Analysis Tools
- **Vigenère Detection** - Key length identification using IoC and Kasiski
- **Manual Substitution** - Interactive letter mapping with frequency analysis

#### Meta Features
- **Try All (Fast)** - Automatically tries multiple cipher types

### Advanced Analysis

- **Index of Coincidence (IoC)** - Statistical measure for cipher identification
- **Frequency Analysis** - Letter and bigram distribution
- **Automatic Cipher Detection** - Heuristic identification of cipher type
- **Smart Scoring** - AI-powered English text recognition using:
  - Chi-squared frequency analysis
  - Common word detection (3000+ words)
  - N-gram pattern matching
  - Vowel ratio validation
  - Consonant cluster detection

### User Interface

- **Dual Theme** - Dark and light modes with automatic system theme detection
- **Settings Dropdown** - Streamlined settings menu with all options
- **Live Updates** - Real-time decryption as you type
- **Side-by-Side Diff** - Visual comparison with highlighted differences
- **Interactive Table** - Sortable results with score ranking
- **Keyboard Shortcuts** - Fast workflow with comprehensive shortcuts
- **Settings Persistence** - Remembers your preferences

## Installation

### Requirements
- Python 3.8 or higher
- tkinter (usually included with Python)

### Setup

```bash
# Clone or download the repository
cd Caesar

# Run the application
python main.py
```

No additional dependencies required! Uses only Python standard library.

## Usage

### Quick Start

1. **Enter text** in the input box (ciphertext or plaintext)
2. **Select cipher type** from the dropdown menu
3. **Click "Break / Apply"** or press `Ctrl+Enter`
4. **Review results** sorted by score
5. **Copy** the best result or export to file

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + Enter` | Break cipher / Apply |
| `Ctrl/Cmd + K` | Clear all |
| `Ctrl/Cmd + B` | Copy best result |
| `Ctrl/Cmd + S` | Load sample |
| `Ctrl/Cmd + E` | Export selected to input |
| `Ctrl/Cmd + Shift + E` | Export to file |
| `Ctrl/Cmd + T` | Toggle theme (Light/Dark) |

### Manual Substitution Mode

1. Select **Substitution (manual)** cipher
2. Click **"Suggest by frequency"** for automatic mapping
3. **Click letter boxes** to type plaintext mappings
4. **Right-click** to lock/unlock letters
5. Watch **live preview** update as you map

### Tips for Best Results

- **Longer text** = More accurate scoring (50+ characters recommended)
- **Try "Try All (Fast)"** if you're unsure of the cipher type
- Use **Analysis panel** to check IoC and get cipher hints
- **Lock letters** in substitution mode to preserve known mappings
- Check **side-by-side diff** to see exactly what changed

## Configuration

Settings are automatically saved to `~/.caesar_cipher/config.json`:

```json
{
  "theme": "dark",
  "keep_case": true,
  "keep_punct": true,
  "auto_select_best": true,
  "show_all": false,
  "top_n": 50,
  "last_cipher": "Caesar",
  "window_geometry": "1200x800+100+100"
}
```

## Architecture

### Core Modules

- **cipher.py** - Cipher implementations and brute force engine
- **scoring.py** - English text scoring with caching
- **analysis_panel.py** - Statistical analysis (IoC, frequency, detection)
- **substitution_helper.py** - Interactive substitution solver
- **vigenere_detect.py** - Vigenère key length detection
- **widgets.py** - Custom UI components (table, toast, diff view)
- **theme.py** - Dark/light theme system
- **config.py** - Settings persistence
- **utils.py** - Helper functions

### Performance Optimizations

- **LRU caching** on scoring function (1024 results)
- **Lazy evaluation** of cipher results
- **Truncation** of large texts in diff view (6000 chars)
- **Top N limiting** to prevent UI lag

## Testing

Run the comprehensive test suite:

```bash
python test_ciphers.py
```

Tests cover:
- All cipher implementations
- Scoring accuracy
- Analysis functions (IoC, detection)
- Error handling
- Sample validation

## Examples

### Breaking a Caesar Cipher

```
Input (ciphertext):  Khoor Zruog! Frgh lv ixq.
Cipher: Caesar
Result: Hello World! Code is fun.
Key: -3
Score: 89.4
```

### Detecting Vigenère Key

```
Input: LXFOPVEFRNHR...
Cipher: Vigenere (detect)
Analysis: 
  IoC best: 4:0.062, 8:0.061, 12:0.059
  Kasiski factors: 4(12), 8(8), 12(6)
  Hint: Key length likely 4
```

### Manual Substitution

```
Ciphertext: KHOOR
Frequency suggest: K→E, H→T, O→A, R→O
Manual adjust: H→E, R→L
Result: HELLO
```

## Known Limitations

- **Vigenère** - Detection only (not full breaking)
- **Playfair** - Not yet implemented
- **Modern ciphers** - AES, RSA not supported
- **Very short texts** - May produce inaccurate scores (<20 chars)

## Future Enhancements

- [ ] Full Vigenère breaking with key recovery
- [ ] Playfair cipher support
- [ ] Columnar transposition with unknown key length
- [ ] Export to multiple formats (CSV, JSON, HTML)
- [ ] Batch processing of multiple texts
- [ ] Custom word lists for scoring
- [ ] Regex-based crib dragging
- [ ] Historical cipher support (Enigma simulation)

## Contributing

Contributions welcome! Areas of interest:

1. **New cipher implementations**
2. **Improved scoring algorithms**
3. **UI/UX enhancements**
4. **Performance optimizations**
5. **Documentation and examples**

## License

MIT License - feel free to use, modify, and distribute.

## Credits

Developed with ❤️ for cryptography enthusiasts, students, and puzzle solvers.

**Scoring algorithm** based on:
- Chi-squared frequency analysis
- Common English word patterns
- N-gram statistics (bigrams, trigrams)
- Phonetic validation (vowel ratios, consonant clusters)

**Vigenère detection** uses:
- Index of Coincidence (Friedman test)
- Kasiski examination

## Changelog

### Version 3.0 (January 2026)
- ✨ **Settings Dropdown Menu** - Replaced popup with streamlined dropdown
- ✨ **System Theme Detection** - Automatically matches macOS light/dark mode on startup
- ✨ **Improved Light Mode** - White text boxes with black text for better readability
- ✨ **Default Cipher** - "Try All (Fast)" now the default selection
- 🎨 Direct palette access for text widgets (more reliable theme switching)
- 🐛 Fixed text widget theming issues
- 📚 Comprehensive documentation updates

### Version 2.0 (January 2026)
- ✨ Added Rail Fence and Columnar transposition ciphers
- ✨ Added Reverse cipher
- ✨ Implemented "Try All (Fast)" meta-cipher
- ✨ Added Index of Coincidence and cipher type detection
- ✨ Frequency-based substitution suggestions
- ✨ Settings persistence with config file
- ✨ Enhanced keyboard shortcuts (cross-platform)
- ✨ Export results to file
- ✨ Comprehensive error handling
- ✨ LRU caching on scoring function
- ✨ Complete test suite with 24 tests
- 🐛 Fixed Try All cipher not implemented
- 🎨 Improved theme system
- 📚 Added detailed README

### Version 1.0
- Initial release with Caesar, Affine, Atbash, ROT47, ROT5
- Basic GUI with results table
- Substitution helper
- Vigenère detection
- Dark theme

## Support

Found a bug? Have a suggestion?

- 🐛 Report issues
- 💡 Request features
- 📖 Check documentation
- 💬 Ask questions

---

**Happy cipher breaking!** 🔐🔓
