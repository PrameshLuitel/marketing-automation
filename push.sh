#!/bin/bash
# Quick push script to update GitHub repository
# Usage: ./push.sh "Your commit message"

MESSAGE=${1:-"Update: $(date '+%Y-%m-%d %H:%M:%S')"}

echo "🔄 Adding all changes..."
git add .

echo "📝 Committing with message: $MESSAGE"
git commit -m "$MESSAGE"

echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Done! Your changes are now on GitHub."
echo "📦 Repository: https://github.com/PrameshLuitel/marketing-automation"
