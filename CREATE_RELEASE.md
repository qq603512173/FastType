# 创建 GitHub Release 详细指南

## 问题：提示 "Make sure you have a valid tag"

这个错误是因为创建 Release 时必须先有一个有效的 tag（版本标签）。

## 解决方案（选择一种）

### 方法一：在 GitHub 网页上直接创建（最简单）✅

1. **访问 Releases 页面：**
   - 打开：`https://github.com/qq603512173/FastType/releases`
   - 点击 "Create a new release" 按钮

2. **创建新标签：**
   - 在 "Choose a tag" 下拉框中，如果显示 "No existing tags"
   - **点击输入框，直接输入新标签名**，例如：`v1.0.0`
   - 或者点击 "Create new tag" 链接
   - **重要：** 确保标签名格式正确（建议：`v1.0.0`、`v1.0.1` 等）

3. **填写其他信息：**
   - **Release title（标题）**：`FastType v1.0.0`（可选）
   - **Description（描述）**：填写版本说明（可选）

4. **上传 exe 文件：**
   - 在 "Attach binaries" 区域，拖拽或选择 `dist/FastType.exe` 文件

5. **发布：**
   - 点击 "Publish release" 按钮
   - GitHub 会自动创建 tag 并发布 Release

### 方法二：先创建 tag，再创建 Release

1. **在本地仓库创建并推送 tag：**
   ```bash
   # 进入项目目录
   cd d:\tools\FastType
   
   # 创建标签（确保代码已提交）
   git tag v1.0.0
   
   # 推送标签到 GitHub
   git push origin v1.0.0
   ```

2. **然后在 GitHub 网页上创建 Release：**
   - 访问：`https://github.com/qq603512173/FastType/releases`
   - 点击 "Create a new release"
   - 在 "Choose a tag" 下拉框中选择 `v1.0.0`
   - 填写标题和描述
   - 上传 exe 文件
   - 点击 "Publish release"

## 常见问题

### Q: 标签名格式有什么要求？
A: 
- 建议使用语义化版本：`v1.0.0`、`v1.0.1`、`v1.1.0`、`v2.0.0`
- 必须以字母或数字开头
- 可以包含字母、数字、点号（.）、连字符（-）
- 避免使用空格和特殊字符

### Q: 如果标签已存在怎么办？
A: 
- 如果标签已存在，可以选择该标签创建新的 Release
- 或者创建新的标签（如 `v1.0.1`）

### Q: 如何查看已有的标签？
A: 
- 在 Releases 页面的 "Choose a tag" 下拉框中查看
- 或访问：`https://github.com/qq603512173/FastType/tags`

## 验证

创建成功后，访问以下链接确认：
- Release 页面：`https://github.com/qq603512173/FastType/releases`
- 下载页面会自动更新：`https://qq603512173.github.io/FastType/`
