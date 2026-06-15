@echo off
echo Starting push to GitHub...

git config user.email "qq849693559@qq.com"
git config user.name "qq849693559"

git add .

git commit -m "feat: Add cross-platform Python app build system"

echo Pushing to GitHub...
git push -u origin main

if %errorlevel% neq 0 (
    echo Push failed, trying SSH...
    git remote set-url origin git@github.com:qq849693559/Windows-Android-.git
    git push -u origin main
)

echo Push completed!
pause