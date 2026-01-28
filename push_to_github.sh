#!/bin/bash
# Quick script to push Caesar Cipher Breaker to GitHub
# Replace YOUR_USERNAME with your actual GitHub username

echo "🚀 Caesar Cipher Breaker - GitHub Push Script"
echo "=============================================="
echo ""

# Check if remote already exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "✅ Remote 'origin' already configured"
    git remote -v
else
    echo "⚠️  No remote configured. Please run:"
    echo ""
    echo "For HTTPS:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/Caesar.git"
    echo ""
    echo "For SSH:"
    echo "  git remote add origin git@github.com:YOUR_USERNAME/Caesar.git"
    echo ""
    exit 1
fi

echo ""
echo "Checking current branch..."
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

echo ""
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "Next steps:"
    echo "1. Go to your repository on GitHub"
    echo "2. Add a description and topics"
    echo "3. Create your first release (v3.0.0)"
    echo "4. Add screenshots to README"
    echo ""
    echo "Repository should be at: https://github.com/YOUR_USERNAME/Caesar"
else
    echo ""
    echo "❌ Push failed. Please check:"
    echo "   - Your GitHub credentials"
    echo "   - Repository permissions"
    echo "   - Remote URL is correct"
fi
