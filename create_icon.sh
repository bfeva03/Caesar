#!/bin/bash

# Script to convert icon.png (1024x1024) to icon.icns for macOS app

# Check if icon.png exists
if [ ! -f "icon.png" ]; then
    echo "❌ Error: icon.png not found in current directory"
    echo "Please save your Caesar coin image as 'icon.png' (1024x1024 pixels)"
    exit 1
fi

# Check image dimensions
SIZE=$(sips -g pixelWidth -g pixelHeight icon.png | grep -E "pixelWidth|pixelHeight" | awk '{print $2}' | tr '\n' 'x' | sed 's/x$//')
echo "📏 Icon dimensions: $SIZE"

# Create iconset directory
echo "📁 Creating icon.iconset directory..."
mkdir -p icon.iconset

# Generate all required icon sizes
echo "🔄 Generating icon sizes..."
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png > /dev/null
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png > /dev/null
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png > /dev/null
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png > /dev/null
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png > /dev/null
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png > /dev/null
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png > /dev/null
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png > /dev/null
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png > /dev/null
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png > /dev/null

echo "✅ Generated $(ls icon.iconset | wc -l | tr -d ' ') icon files"

# Convert to icns
echo "🎨 Converting to .icns format..."
iconutil -c icns icon.iconset

# Check if successful
if [ -f "icon.icns" ]; then
    echo "✅ Success! Created icon.icns"
    echo "📦 File size: $(du -h icon.icns | cut -f1)"
    
    # Optional: Clean up iconset directory
    read -p "🗑️  Remove temporary icon.iconset folder? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf icon.iconset
        echo "✅ Cleaned up temporary files"
    fi
else
    echo "❌ Error: Failed to create icon.icns"
    exit 1
fi

echo ""
echo "🎉 Done! Your icon.icns is ready for use in setup.py"
