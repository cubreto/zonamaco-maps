#!/bin/bash
# ZonaMaco Maps - Quick Deploy Script

echo "🎨 ZonaMaco 2026 Maps - Deployment"
echo "=================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "ZonaMaco 2026 VIP Maps - Initial commit"
    git branch -M main
fi

echo ""
echo "Choose deployment platform:"
echo "1) GitHub Pages (static, free)"
echo "2) Render.com (free tier)"
echo "3) Vercel (free)"
echo "4) Heroku"
echo "5) Local only"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        read -p "Enter your GitHub username: " username
        repo_name="zonamaco-maps"

        echo "Creating GitHub repo..."
        gh repo create $repo_name --public --source=. --push 2>/dev/null || {
            echo "Note: If repo exists, pushing to it..."
            git remote add origin "https://github.com/$username/$repo_name.git" 2>/dev/null
            git push -u origin main
        }

        echo ""
        echo "✅ Code pushed! Now enable GitHub Pages:"
        echo "   1. Go to: https://github.com/$username/$repo_name/settings/pages"
        echo "   2. Source: Deploy from branch"
        echo "   3. Branch: main, Folder: /docs"
        echo "   4. Save"
        echo ""
        echo "🌐 Your site will be at: https://$username.github.io/$repo_name/"
        ;;
    2)
        echo ""
        echo "Push to GitHub first, then:"
        echo "1. Go to https://render.com"
        echo "2. New → Web Service → Connect GitHub"
        echo "3. Select this repo"
        echo "4. render.yaml will auto-configure"
        ;;
    3)
        echo ""
        if command -v vercel &> /dev/null; then
            vercel
        else
            echo "Install Vercel CLI: npm i -g vercel"
            echo "Then run: vercel"
        fi
        ;;
    4)
        echo ""
        if command -v heroku &> /dev/null; then
            heroku create zonamaco-maps-$(date +%s)
            git push heroku main
            heroku open
        else
            echo "Install Heroku CLI first: brew install heroku/brew/heroku"
        fi
        ;;
    5)
        echo ""
        echo "Running locally..."
        pip install -r requirements.txt
        python app.py
        ;;
esac
