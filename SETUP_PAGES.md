# GitHub Pages 设置指南

## 快速设置步骤

### 1. 下载链接已配置 ✅

`index.html` 文件中的下载链接已配置为你的 GitHub 仓库：
- GitHub 仓库：`qq603512173/FastType`
- Releases 链接：`https://github.com/qq603512173/FastType/releases/latest`
- 下载页面：`https://qq603512173.github.io/FastType/`

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

**重要说明：**
- exe 文件上传到 **GitHub Releases**，不是直接上传到代码仓库
- Releases 是 GitHub 的版本发布功能，文件作为附件存储
- exe 文件**不会**出现在代码仓库的文件列表中（如 `dist/` 目录）
- 用户可以通过 Releases 页面或下载页面的按钮下载

**操作步骤：**

1. **本地打包：**
   ```bash
   pyinstaller FastType.spec
   ```
   生成的 exe 在 `dist/FastType.exe`

2. **创建 Release（两种方法）：**

   **方法一：在 GitHub 网页上创建（推荐，最简单）**
   - 在 GitHub 仓库页面，点击右侧 "Releases" 链接
   - 或直接访问：`https://github.com/qq603512173/FastType/releases`
   - 点击 "Create a new release" 或 "Draft a new release"
   - **重要：** 在 "Choose a tag" 下拉框中：
     - 如果下拉框是空的，点击 "Create new tag" 或直接在输入框输入新标签名（如 `v1.0.0`）
     - 输入标签名后，选择 "Create new tag on publish" 或类似选项
     - 标签格式建议：`v1.0.0`、`v1.0.1` 等（以 `v` 开头）

   **方法二：先创建 tag，再创建 Release**
   ```bash
   # 在本地仓库目录执行
   git tag v1.0.0
   git push origin v1.0.0
   ```
   然后再在 GitHub 网页上创建 Release，此时下拉框中会有 `v1.0.0` 可选

3. **填写 Release 信息：**
   - **Tag version（标签）**：选择或输入版本号，如 `v1.0.0`（必须填写，不能为空）
   - **Release title（标题）**：如 "FastType v1.0.0"（可选，默认使用 tag 名）
   - **Description（描述）**：填写更新说明（可选）

4. **上传 exe 文件：**
   - 在 "Attach binaries" 区域，拖拽或点击上传 `dist/FastType.exe` 文件
   - 文件会自动上传到 GitHub 服务器

5. **发布：**
   - 点击 "Publish release" 按钮
   - Release 创建后，exe 文件会出现在该 Release 的下载列表中

**查看 Release：**
- Release 页面：`https://github.com/qq603512173/FastType/releases`
- 下载页面会自动从 Releases 获取最新版本的下载链接

### 4. 访问下载页面

设置完成后，访问：`https://qq603512173.github.io/FastType/`

页面会自动从 GitHub Releases 获取最新版本的下载链接。

## 注意事项

- 确保 `index.html` 文件在仓库根目录
- 首次部署可能需要几分钟时间
- 如果使用自定义域名，需要在仓库 Settings → Pages 中配置
