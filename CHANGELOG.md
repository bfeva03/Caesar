# Changelog

All notable changes to Caesar Cipher Breaker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-01-28

### Added
- **New Ciphers**:
  - Rail Fence cipher with rail count brute force
  - Columnar Transposition cipher
  - Reverse cipher (simple text reversal)
  - Try All (Fast) meta-cipher for quick analysis
- **Settings Persistence**: All user preferences now saved automatically
- **Index of Coincidence (IoC)**: Statistical analysis for cipher identification
- **Cipher Type Detection**: Automatic heuristic identification
- **Frequency Analysis Suggestion**: Auto-mapping for substitution ciphers
- **Keyboard Shortcuts**: Full cross-platform shortcuts (Cmd/Ctrl)
- **Enhanced Analysis Panel**: Shows IoC and detection hints

### Changed
- **Performance**: LRU caching for scoring with 1024 result limit
- **UI**: Streamlined settings dropdown menu
- **Scoring**: Improved English text recognition with smarter algorithms
- **Error Handling**: Comprehensive try-except blocks throughout codebase

### Fixed
- Try All (Fast) cipher now properly implemented
- Escaped quote syntax errors corrected
- Substitution helper tracking issues resolved
- Settings persistence across sessions

### Performance
- Transposition ciphers limited to top 100 results
- Efficient caching reduces redundant calculations
- Smart scoring algorithm optimizations

## [2.0.0] - Previous Release

### Added
- Dual theme support (Dark/Light)
- Manual substitution helper with live preview
- Vigenère cipher detection
- Automatic cipher scoring system
- Side-by-side diff view
- Export functionality

### Changed
- Complete UI redesign with modern interface
- Improved frequency analysis display

## [1.0.0] - Initial Release

### Added
- Caesar cipher breaking
- Affine cipher support
- Basic ROT ciphers (ROT13, ROT47, ROT5)
- Atbash cipher
- Frequency analysis
- Basic UI with tkinter
