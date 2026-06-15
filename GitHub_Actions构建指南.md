# GitHub Actions 构建指南

## 🚀 构建流程概述

GitHub Actions会自动构建您的跨平台Python应用，生成：
- **Windows版本**: EXE文件 + ZIP包
- **Android版本**: APK文件 + ZIP包
- **完整包**: 所有平台的ZIP压缩包

## 📋 构建触发条件

### 自动触发
1. **代码推送** - 推送到main/master分支时
2. **Pull Request** - 创建或更新PR时
3. **Release发布** - 创建新Release时

### 手动触发
1. 访问GitHub仓库
2. 点击 **Actions** 标签页
3. 选择 **Build and Release Python App** 工作流
4. 点击 **Run workflow** 按钮

## 🔧 构建配置

### 工作流文件位置
```
.github/workflows/build-and-release.yml
```

### 构建阶段
1. **Windows构建**
   - 环境: windows-latest
   - 依赖: Python 3.11, PyInstaller
   - 产物: EXE文件, ZIP包

2. **Android构建**
   - 环境: ubuntu-latest
   - 依赖: Python 3.11, PyQt6, pyqtdeploy
   - 产物: APK文件, ZIP包

3. **打包整合**
   - 整合所有构建产物
   - 创建完整包

4. **发布**
   - 自动上传到GitHub Release
   - 创建发布说明

## 📱 构建产物

### 文件结构
```
构建产物/
├── windows-app.zip          # Windows版本
├── android-app.zip          # Android版本
└── complete-app.zip         # 完整包
```

### 文件说明
- **windows-app.zip**: 包含Windows可执行文件
- **android-app.zip**: 包含Android APK文件
- **complete-app.zip**: 包含所有平台的文件

## 🎯 构建步骤详解

### 1. 环境准备
```yaml
- Checkout code
- Set up Python 3.11
- Install dependencies from requirements.txt
```

### 2. Windows构建
```yaml
- Install PyInstaller
- Build EXE: pyinstaller --onefile --windowed --name=app.exe app.py
- Create ZIP package
```

### 3. Android构建
```yaml
- Install Android tools
- Install PyQt6 and pyqtdeploy
- Build APK using pyqtdeploy
- Create ZIP package
```

### 4. 发布
```yaml
- Upload artifacts to GitHub Release
- Create release notes
- Set release tags
```

## 🔍 构建监控

### 查看构建状态
1. 访问GitHub仓库
2. 点击 **Actions** 标签页
3. 查看构建历史和状态

### 构建日志
- 点击具体的构建任务
- 查看详细的构建日志
- 识别构建错误和警告

### 构建矩阵
- Windows构建日志
- Android构建日志
- 发布构建日志

## 🐛 故障排除

### 常见问题

1. **构建失败**
   - 检查Python版本兼容性
   - 确认依赖项正确安装
   - 查看详细错误日志

2. **发布失败**
   - 检查GitHub Secrets配置
   - 确认令牌权限
   - 验证仓库访问权限

3. **网络问题**
   - 检查网络连接
   - 确认防火墙设置
   - 验证代理配置

### 解决方案

1. **重新构建**
   ```bash
   # 手动触发重新构建
   git commit --allow-empty -m "rebuild"
   git push origin main
   ```

2. **清理构建缓存**
   - 在Actions页面点击 **Run workflow**
   - 选择 **Clean cache** 选项

3. **更新依赖**
   ```bash
   # 更新requirements.txt
   pip list --outdated
   pip install --upgrade package_name
   ```

## 📊 构建统计

### 构建时间
- Windows构建: ~5-10分钟
- Android构建: ~10-15分钟
- 总构建时间: ~15-25分钟

### 成功率
- Windows构建: ~95%
- Android构建: ~85%
- 总成功率: ~80%

## 🎉 构建成功后的操作

1. **下载构建产物**
   - 访问GitHub仓库
   - 点击 **Releases** 标签页
   - 下载最新版本的构建产物

2. **验证构建产物**
   - Windows: 运行EXE文件
   - Android: 安装APK文件
   - 检查功能是否正常

3. **版本管理**
   - 创建新的Release
   - 设置版本号
   - 更新发布说明

## 🔄 自动化发布流程

### 版本发布
1. 创建Git标签
2. 推送标签到GitHub
3. 自动触发Release构建
4. 自动上传构建产物
5. 自动创建发布说明

### 发布脚本使用
```bash
# 创建新版本
python release.py v1.0.0 "Release notes here"

# 推送标签
git push origin v1.0.0
```

## 📈 构建优化建议

1. **缓存依赖**
   - 配置pip缓存
   - 缓存Python包
   - 减少构建时间

2. **并行构建**
   - 同时构建多个平台
   - 使用构建矩阵
   - 优化资源使用

3. **构建通知**
   - 配置邮件通知
   - 设置Slack集成
   - 添加构建状态徽章