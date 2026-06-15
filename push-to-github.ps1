# PowerShell脚本用于推送代码到GitHub
Write-Host "开始推送代码到GitHub..."

# 设置Git配置
git config user.email "qq849693559@qq.com"
git config user.name "qq849693559"

# 添加所有文件
git add .

# 提交代码
git commit -m "feat: 添加跨平台Python应用构建系统

- 添加GitHub Actions工作流配置
- 支持Windows和Android平台构建
- 配置自动发布到GitHub Releases
- 添加示例Python应用程序
- 包含完整的使用说明"

# 尝试推送
try {
    Write-Host "尝试推送代码..."
    git push origin main
    Write-Host "推送成功！"
} catch {
    Write-Host "推送失败，尝试其他方法..."
    
    # 尝试使用SSH
    try {
        Write-Host "尝试使用SSH推送..."
        git remote set-url origin git@github.com:qq849693559/Windows-Android-.git
        git push origin main
        Write-Host "SSH推送成功！"
    } catch {
        Write-Host "SSH推送也失败了，请检查网络连接"
        Write-Host "可能的原因："
        Write-Host "1. 网络连接问题"
        Write-Host "2. 防火墙阻止"
        Write-Host "3. GitHub访问限制"
        Write-Host "4. 代理设置问题"
        
        # 提供手动操作建议
        Write-Host ""
        Write-Host "建议的手动操作："
        Write-Host "1. 手动打开命令提示符"
        Write-Host "2. 切换到项目目录: cd G:\iFlow CLI"
        Write-Host "3. 执行: git push origin main"
        Write-Host "4. 如果还是失败，尝试使用VPN或更换网络"
    }
}

Write-Host "脚本执行完成"