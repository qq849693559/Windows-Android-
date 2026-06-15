Write-Host "Starting push to GitHub..."

git config user.email "qq849693559@qq.com"
git config user.name "qq849693559"

git add .

git commit -m "feat: Add cross-platform Python app build system"

git push origin main

Write-Host "Push completed!"