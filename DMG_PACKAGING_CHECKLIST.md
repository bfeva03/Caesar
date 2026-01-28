# Caesar Cipher App - DMG Packaging & Shipping Checklist

## 📋 Pre-Packaging Preparation

### Code & Configuration
- [ ] **Version number set** - Update version in app metadata
- [ ] **App icon created** - Create .icns file (1024x1024 PNG → iconutil)
- [ ] **All dependencies documented** - Verify requirements.txt is complete
- [ ] **Code signing certificate obtained** - Apple Developer ID Application certificate
- [ ] **App bundle identifier chosen** - e.g., `com.yourname.caesarcipher`
- [ ] **README and LICENSE files** - Include in package
- [ ] **Remove debug code** - Clean up print statements, test code
- [ ] **Test on clean macOS system** - Verify app works without dev environment

### Files to Create
- [ ] **setup.py** - For py2app configuration
- [ ] **Info.plist** - macOS app metadata
- [ ] **icon.icns** - App icon in macOS format
- [ ] **DMG background image** (optional) - Custom installer appearance

---

## 🔨 Packaging Steps

### Step 1: Install Packaging Tools
```bash
pip install py2app
brew install create-dmg  # Alternative: npm install -g appdmg
```

### Step 2: Create setup.py
- [ ] **Create setup.py file** with py2app configuration
- [ ] **Include all Python files** in packages/py_modules
- [ ] **Specify icon file** and app metadata
- [ ] **Set LSUIElement** if you want menubar-only (no dock icon)
- [ ] **Define plist options** (CFBundleName, CFBundleIdentifier, etc.)

### Step 3: Build the App Bundle
- [ ] **Clean previous builds**: `rm -rf build dist`
- [ ] **Build in alias mode** (for testing): `python setup.py py2app -A`
- [ ] **Test alias mode app** to verify functionality
- [ ] **Build production version**: `python setup.py py2app`
- [ ] **Verify .app created** in `dist/` folder
- [ ] **Test .app directly** by double-clicking

### Step 4: Code Signing (Required for Distribution)
- [ ] **Sign the app bundle**:
  ```bash
  codesign --deep --force --verify --verbose \
    --sign "Developer ID Application: Your Name (TEAMID)" \
    --options runtime \
    dist/Caesar.app
  ```
- [ ] **Verify signature**: `codesign --verify --deep --verbose=2 dist/Caesar.app`
- [ ] **Check signature details**: `codesign -dv --verbose=4 dist/Caesar.app`

### Step 5: Create DMG
- [ ] **Create DMG with create-dmg**:
  ```bash
  create-dmg \
    --volname "Caesar Cipher" \
    --volicon "icon.icns" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "Caesar.app" 200 190 \
    --hide-extension "Caesar.app" \
    --app-drop-link 600 185 \
    "Caesar-Installer.dmg" \
    "dist/Caesar.app"
  ```
- [ ] **OR use hdiutil** (built-in macOS tool):
  ```bash
  # Create temporary folder
  mkdir dmg_temp
  cp -R dist/Caesar.app dmg_temp/
  ln -s /Applications dmg_temp/Applications
  
  # Create DMG
  hdiutil create -volname "Caesar Cipher" \
    -srcfolder dmg_temp \
    -ov -format UDZO \
    Caesar-Installer.dmg
  
  # Cleanup
  rm -rf dmg_temp
  ```

### Step 6: Sign the DMG
- [ ] **Sign DMG file**:
  ```bash
  codesign --sign "Developer ID Application: Your Name (TEAMID)" \
    Caesar-Installer.dmg
  ```
- [ ] **Verify DMG signature**: `codesign --verify Caesar-Installer.dmg`

### Step 7: Notarization (For Gatekeeper)
- [ ] **Store credentials** (one-time):
  ```bash
  xcrun notarytool store-credentials "AC_PASSWORD" \
    --apple-id "your-email@example.com" \
    --team-id TEAMID \
    --password "app-specific-password"
  ```
- [ ] **Submit for notarization**:
  ```bash
  xcrun notarytool submit Caesar-Installer.dmg \
    --keychain-profile "AC_PASSWORD" \
    --wait
  ```
- [ ] **Check notarization status** if not using --wait
- [ ] **Staple notarization ticket** (after approval):
  ```bash
  xcrun stapler staple Caesar-Installer.dmg
  ```
- [ ] **Verify stapling**: `xcrun stapler validate Caesar-Installer.dmg`

---

## ✅ Testing Checklist

### Pre-Distribution Testing
- [ ] **Mount DMG** - Verify DMG opens correctly
- [ ] **Test drag-to-Applications** - Drag app to Applications folder
- [ ] **Launch from Applications** - Double-click to launch
- [ ] **Test first launch** - Verify no permission issues
- [ ] **Test all features** - Encrypt, decrypt, brute force, analysis
- [ ] **Check menu bar integration** - If using system theme detection
- [ ] **Test on different macOS versions**:
  - [ ] macOS Monterey (12.x)
  - [ ] macOS Ventura (13.x)
  - [ ] macOS Sonoma (14.x)
  - [ ] macOS Sequoia (15.x)
- [ ] **Test on fresh Mac** - No development tools installed
- [ ] **Test offline installation** - No internet connection required

### Security & Permissions
- [ ] **Gatekeeper allows launch** - No "unidentified developer" warning
- [ ] **No quarantine issues** - App isn't blocked on first launch
- [ ] **File permissions work** - Can save/load files
- [ ] **Clipboard access works** - Copy/paste functionality

---

## 📦 Distribution Checklist

### File Preparation
- [ ] **Final DMG renamed** - e.g., `Caesar-Cipher-v1.0.dmg`
- [ ] **Calculate checksums**:
  ```bash
  shasum -a 256 Caesar-Cipher-v1.0.dmg > Caesar-Cipher-v1.0.dmg.sha256
  ```
- [ ] **Create release notes** - Document new features, changes, fixes
- [ ] **Prepare screenshots** - For website/distribution page
- [ ] **Update README** - Installation instructions

### Distribution Channels
- [ ] **Upload to GitHub Releases** - If using GitHub
- [ ] **Upload to personal website** - Direct download link
- [ ] **Update download page** - Include system requirements
- [ ] **Create installation guide** - Step-by-step for end users
- [ ] **Announce release** - Social media, mailing list, etc.

### Documentation to Include
- [ ] **System Requirements**:
  - macOS 10.13 or later
  - Python bundled (no user installation needed)
  - Disk space requirements
- [ ] **Installation Instructions**:
  1. Download DMG file
  2. Open DMG
  3. Drag Caesar app to Applications folder
  4. Launch from Applications
- [ ] **Troubleshooting section**
- [ ] **Contact/support information**

---

## 🔍 Quality Assurance

### Final Checks Before Release
- [ ] **All links work** - README, documentation
- [ ] **Version numbers match** - App, DMG filename, documentation
- [ ] **License file included**
- [ ] **Credits/attributions included**
- [ ] **No hardcoded paths** - App works from any location
- [ ] **Clean uninstall process** - Document how to remove app
- [ ] **Privacy policy** (if applicable) - Data collection disclosure
- [ ] **Backup original source** - Before releasing

### Post-Release
- [ ] **Monitor user feedback** - GitHub issues, email
- [ ] **Track downloads** - Analytics if available
- [ ] **Prepare update mechanism** - How users get new versions
- [ ] **Document known issues** - Create issue tracker

---

## 🛠️ Troubleshooting Common Issues

### Build Issues
- **Missing modules**: Add to `packages` in setup.py
- **Icon not showing**: Verify .icns format and path in setup.py
- **App won't launch**: Check console logs in `/Applications/Utilities/Console.app`
- **Import errors**: Use `--packages` flag in py2app options

### Code Signing Issues
- **"identity not found"**: Verify certificate in Keychain Access
- **Signature invalid**: Use `--deep --force` and ensure all frameworks signed
- **Gatekeeper blocks app**: Complete notarization process

### Notarization Issues
- **Upload fails**: Check file size limits, network connection
- **Notarization rejected**: Review error log with `notarytool log`
- **Common rejections**: Unsigned frameworks, hardened runtime issues

### Distribution Issues
- **DMG won't mount**: Verify with Disk Utility
- **"damaged" error**: Notarization or signature issue
- **Slow downloads**: Consider CDN or compression

---

## 📚 Resources

- **py2app documentation**: https://py2app.readthedocs.io/
- **create-dmg GitHub**: https://github.com/create-dmg/create-dmg
- **Apple Developer**: https://developer.apple.com/
- **Code Signing Guide**: https://developer.apple.com/support/code-signing/
- **Notarization Guide**: https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution

---

## 📝 Notes

- **Apple Developer Account Required**: For code signing and notarization ($99/year)
- **Alternative for Free Distribution**: Users will see "unidentified developer" warning
- **Estimated Time**: First-time setup: 4-6 hours | Subsequent builds: 30-60 minutes
- **DMG Size**: Expect ~30-50MB for bundled Python app

---

**Next Steps**: Start with "Pre-Packaging Preparation" section and work through each checklist item systematically.
