# Python跨平台应用构建系统

基于GitHub Actions + GitHub Releases的自动化构建系统，支持Windows和Android平台。

## 项目结构

```
├── .github/workflows/
│   └── build-and-release.yml    # GitHub Actions工作流配置
├── app.py                      # 主应用程序
├── requirements.txt            # Python依赖
├── android-project.pdy         # Android项目配置
├── release.py                  # 发布脚本
└── README.md                  # 说明文档
```

## 功能特性

- ✅ **多平台构建**: Windows (EXE) + Android (APK)
- ✅ **自动化部署**: GitHub Actions自动构建
- ✅ **版本管理**: 自动创建GitHub Releases
- ✅ **打包格式**: 支持ZIP和原生格式
- ✅ **CI/CD集成**: 完整的持续集成流程

## 构建流程

### 1. 代码提交触发
```bash
git add .
git commit -m "feat: 添加新功能"
git push origin main
```

### 2. GitHub Actions自动构建
- Windows平台构建EXE
- Android平台构建APK
- 自动打包ZIP文件
- 上传构建产物

### 3. 手动发布版本
```bash
# 创建标签
git tag -a v1.0.0 -m "Release v1.0.0"

# 推送标签
git push origin v1.0.0

# 运行发布脚本
python release.py v1.0.0
```

## 配置说明

### GitHub Actions工作流
- **Windows构建**: 使用Windows环境，生成EXE文件
- **Android构建**: 使用Ubuntu环境，生成APK文件
- **Release发布**: 自动上传构建产物到GitHub Release

### 环境变量
- `GITHUB_TOKEN`: GitHub个人访问令牌
- `GITHUB_REPOSITORY`: 仓库地址 (可选)

## 自定义配置

### 修改应用名称
编辑 `app.py` 文件中的窗口标题和应用程序名称。

### 修改依赖项
编辑 `requirements.txt` 文件，添加所需的Python包。

### 修改Android配置
编辑 `android-project.pdy` 文件，调整Android相关设置。

## 构建产物

每次构建会生成以下文件：
- `windows-app.zip` - Windows版本
- `android-app.zip` - Android版本  
- `complete-app.zip` - 完整包

## 故障排除

### 常见问题

1. **构建失败**
   - 检查Python版本兼容性
   - 确认依赖项正确安装
   - 查看GitHub Actions日志

2. **发布失败**
   - 确认GitHub令牌权限
   - 检查仓库访问权限
   - 验证标签格式

3. **Android构建问题**
   - 确保Android SDK已安装
   - 检查PyQtdeploy配置
   - 验证签名配置

## 下一步

1. **本地测试**: 在本地运行 `python app.py` 测试应用
2. **配置GitHub**: 将代码推送到GitHub仓库
3. **设置Secrets**: 在GitHub仓库设置中添加GITHUB_TOKEN
4. **触发构建**: 提交代码或创建标签触发构建

## 支持

如有问题，请查看GitHub Actions日志或提交Issue。