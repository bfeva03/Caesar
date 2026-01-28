# Caesar Cipher Breaker v3.0.0 - Release Notes

## 🎉 Major Release - January 28, 2026

This is a significant update with new ciphers, powerful analysis tools, and a modernized interface.

### 🆕 What's New

#### New Cipher Types
- **Rail Fence Cipher** - Zigzag transposition with automatic rail count detection
- **Columnar Transposition** - Column-based permutation cipher
- **Reverse Cipher** - Simple text reversal
- **Try All (Fast)** - Meta-cipher that tests multiple algorithms automatically

#### Advanced Analysis Tools
- **Index of Coincidence (IoC)** - Statistical measure for identifying cipher types
- **Automatic Cipher Detection** - Smart heuristics to identify monoalphabetic, polyalphabetic, or transposition ciphers
- **Frequency-Based Mapping** - Auto-suggest letter mappings for substitution ciphers
- **Enhanced Scoring Algorithm** - More accurate English text recognition

#### User Experience
- **Settings Persistence** - All preferences saved automatically between sessions
- **Comprehensive Keyboard Shortcuts** - Full Cmd/Ctrl support for all major actions
- **Improved Analysis Panel** - Shows IoC values and detection hints
- **Better Error Handling** - Graceful error recovery throughout

### 🚀 Performance Improvements
- **LRU Caching** - Scoring results cached for faster repeated operations
- **Smart Limiting** - Transposition ciphers limited to top 100 results
- **Optimized Algorithms** - Reduced redundant calculations

### 🐛 Bug Fixes
- Fixed "Try All (Fast)" implementation
- Corrected escaped quote syntax errors
- Resolved substitution helper tracking issues
- Fixed settings persistence across sessions

### 📦 Distribution
- **macOS App Bundle** - Double-click installation
- **Universal Binary** - Supports both Intel (x86_64) and Apple Silicon (arm64)
- **Disk Image (DMG)** - Professional installer with drag-and-drop

### 📊 Technical Details
- **App Size**: 61 MB (bundle), 29 MB (compressed DMG)
- **Python Version**: 3.14
- **macOS Requirement**: 10.13+ (High Sierra or later)
- **Dependencies**: Python standard library only (no external packages)

### 🔐 Security
- **Code Signed** - All binaries automatically signed
- **Checksum**: `4b6587fee449cf52f51a7c575599fb992351843a3f5233914a3fa809404401c7`

### 📚 Documentation
- Complete README with usage examples
- Contributing guidelines for developers
- Security policy for vulnerability reporting
- GitHub issue templates for bugs, features, and cipher requests

### 🙏 Acknowledgments
This release represents a complete overhaul of the Caesar Cipher Breaker with a focus on usability, performance, and extensibility.

### 📝 Installation

#### From DMG (Recommended)
1. Download `Caesar-Cipher-Installer.dmg`
2. Open the DMG file
3. Drag "Caesar Cipher" to Applications folder
4. Launch from Applications

#### From Source
```bash
git clone https://github.com/YOUR_USERNAME/Caesar.git
cd Caesar
python main.py
```

### 🐞 Known Issues
- First launch may show Gatekeeper warning (unsigned distribution)
  - **Workaround**: Right-click → Open → confirm
- Some advanced features require macOS 10.13+

### 🔮 Coming Soon
See [IMPROVEMENTS.md](IMPROVEMENTS.md) for planned features and enhancement ideas.

### 🔗 Links
- **GitHub Repository**: https://github.com/YOUR_USERNAME/Caesar
- **Report Issues**: https://github.com/YOUR_USERNAME/Caesar/issues
- **License**: MIT License

---

**Full Changelog**: See [CHANGELOG.md](CHANGELOG.md) for complete version history.
