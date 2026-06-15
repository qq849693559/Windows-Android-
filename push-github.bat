@echo off
echo 开始推送代码到GitHub...

git config user.email "qq849693559@qq.com"
git config user.name "qq849693559"

git add .

git commit -m "feat: 添加完整的跨平台Python应用构建系统"

echo 正在推送到GitHub...
git push -u origin main

if %errorlevel% neq 0 (
    echo 推送失败，尝试使用SSH...
    git remote set-url origin git@github.com:qq849693559/Windows-Android-.git
    git push -u origin main
)

echo 推送完成！
pause