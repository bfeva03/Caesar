#!/bin/bash

# Script to build Caesar Cipher app and package it as a DMG
# This is a complete build process from source to DMG

set -e  # Exit on error

echo "🚀 Caesar Cipher App Builder"
echo "================================"
echo ""

# Configuration
APP_NAME="Caesar Cipher"
DMG_NAME="Caesar-Cipher-Installer"
VERSION="1.0.0"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Clean previous builds
echo -e "${BLUE}📦 Step 1: Cleaning previous builds...${NC}"
rm -rf build dist
echo -e "${GREEN}✅ Cleaned build directories${NC}"
echo ""

# Step 2: Check for py2app
echo -e "${BLUE}🔍 Step 2: Checking dependencies...${NC}"
if ! python3 -c "import py2app" 2>/dev/null; then
    echo -e "${RED}❌ py2app not found${NC}"
    echo "Installing py2app..."
    pip install py2app
fi
echo -e "${GREEN}✅ py2app installed${NC}"
echo ""

# Step 3: Build the app
echo -e "${BLUE}🔨 Step 3: Building .app bundle with py2app...${NC}"
python3 setup.py py2app
echo -e "${GREEN}✅ App bundle created: dist/${APP_NAME}.app${NC}"
echo ""

# Step 4: Verify app bundle
echo -e "${BLUE}🔍 Step 4: Verifying app bundle...${NC}"
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo -e "${RED}❌ Error: App bundle not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ App bundle verified${NC}"
echo ""

# Step 5: Create DMG
echo -e "${BLUE}💿 Step 5: Creating DMG installer...${NC}"

# Check if create-dmg is available
if command -v create-dmg &> /dev/null; then
    echo "Using create-dmg tool..."
    create-dmg \
        --volname "${APP_NAME}" \
        --volicon "icon.icns" \
        --window-pos 200 120 \
        --window-size 800 400 \
        --icon-size 100 \
        --icon "${APP_NAME}.app" 200 190 \
        --hide-extension "${APP_NAME}.app" \
        --app-drop-link 600 185 \
        "${DMG_NAME}.dmg" \
        "dist/${APP_NAME}.app"
else
    # Fallback to hdiutil (built-in macOS tool)
    echo "Using hdiutil (built-in macOS tool)..."
    
    # Create temporary directory
    mkdir -p dmg_temp
    cp -R "dist/${APP_NAME}.app" dmg_temp/
    ln -s /Applications dmg_temp/Applications
    
    # Create DMG
    hdiutil create -volname "${APP_NAME}" \
        -srcfolder dmg_temp \
        -ov -format UDZO \
        "${DMG_NAME}.dmg"
    
    # Cleanup
    rm -rf dmg_temp
fi

echo -e "${GREEN}✅ DMG created: ${DMG_NAME}.dmg${NC}"
echo ""

# Step 6: Get DMG info
echo -e "${BLUE}📊 Step 6: Build summary${NC}"
echo "--------------------------------"
echo "App Name: ${APP_NAME}"
echo "Version: ${VERSION}"
echo "App Size: $(du -h "dist/${APP_NAME}.app" | tail -1 | cut -f1)"
echo "DMG Size: $(du -h "${DMG_NAME}.dmg" | cut -f1)"
echo "DMG Location: $(pwd)/${DMG_NAME}.dmg"
echo ""

# Step 7: Calculate checksum
echo -e "${BLUE}🔐 Step 7: Generating checksum...${NC}"
shasum -a 256 "${DMG_NAME}.dmg" > "${DMG_NAME}.dmg.sha256"
echo -e "${GREEN}✅ SHA-256: $(cat ${DMG_NAME}.dmg.sha256)${NC}"
echo ""

# Step 8: Test the app
echo -e "${BLUE}🧪 Step 8: Quick test...${NC}"
echo "You can test the app by running:"
echo "  open dist/${APP_NAME}.app"
echo ""
echo "Or test the DMG installer:"
echo "  open ${DMG_NAME}.dmg"
echo ""

echo -e "${GREEN}🎉 Build complete!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Ready for distribution: ${DMG_NAME}.dmg"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚠️  Note: For distribution without Gatekeeper warnings,"
echo "   you'll need to code sign and notarize the app."
echo "   See DMG_PACKAGING_CHECKLIST.md for details."
