# GitHub Pages 设置指南

## 快速设置步骤

### 1. 更新下载链接

编辑 `index.html` 文件，将以下内容中的 `YOUR_USERNAME` 替换为你的 GitHub 用户名：

- 第 189 行：`const repo = 'YOUR_USERNAME/FastType';`
- 第 202 行：`https://github.com/YOUR_USERNAME/FastType/releases/latest`
- 第 207 行：`https://github.com/YOUR_USERNAME/FastType`
- 第 208 行：`https://github.com/YOUR_USERNAME/FastType/issues`

### 2. 启用 GitHub Pages

**方法一：使用 GitHub Actions（推荐，已配置）**

1. 提交 `index.html` 和 `.github/workflows/deploy-pages.yml` 到仓库
2. 在仓库 Settings → Pages
3. Source 选择 "GitHub Actions"
4. 保存后，GitHub Actions 会自动部署页面

**方法二：使用分支部署**

1. 在仓库 Settings → Pages
2. Source 选择 "Deploy from a branch"
3. Branch 选择 `main`，文件夹选择 `/ (root)`
4. 保存

### 3. 上传 exe 到 Releases

1. 本地打包：`pyinstaller FastType.spec`
2. 在 GitHub 仓库页面点击 "Releases" → "Create a new release"
3. 填写版本号（如 `v1.0.0`）和发布说明
4. 上传 `dist/FastType.exe` 文件
5. 点击 "Publish release"

### 4. 访问下载页面

设置完成后，访问：`https://YOUR_USERNAME.github.io/FastType/`

页面会自动从 GitHub Releases 获取最新版本的下载链接。

## 注意事项

- 确保 `index.html` 文件在仓库根目录
- 首次部署可能需要几分钟时间
- 如果使用自定义域名，需要在仓库 Settings → Pages 中配置
