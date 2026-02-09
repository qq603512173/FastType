# FastType

快速输入常用文本的小工具：用快捷键调出，在搜索框输入关键字筛选，选择一条结果后回车，文本会粘贴到当前焦点（如登录框、Shell 等），无需再从记事本复制粘贴。

## 🌐 下载页面

**访问下载页面：** [https://qq603512173.github.io/FastType/](https://qq603512173.github.io/FastType/)

> 提示：启用 GitHub Pages 后即可访问下载页面。

![按 Alt+Q 打开 FastType](build/FastType演示2.gif)
*按 Alt+Q 打开 FastType / Press Alt+Q to open FastType*

## 技术方案：Python + PyQt5

- **PyQt5**：桌面界面（顶部搜索框 + 下方结果列表，类似 Everything）。
- **keyboard**：全局快捷键（`Alt+Q`）和向系统发送按键（`Ctrl+V`），**不依赖浏览器沙箱**，可直接向其他窗口发送按键。
- **pyperclip**：剪贴板读写，粘贴前暂存、粘贴后恢复。
- **数据**：片段保存在 `%USERPROFILE%\.fasttype\snippets.json`（Windows）或 `~/.fasttype/snippets.json`。

## 功能

- **全局快捷键**：`Alt+Q` 调出/显示窗口。
- **搜索**：在顶部搜索框输入关键字，按标题或内容过滤片段。
- **选择**：方向键或鼠标选择一条结果，回车或双击即可将**内容**粘贴到调出 FastType 前的焦点位置。
- **托盘**：支持系统托盘，右键可「显示 FastType」或「退出」。
- **片段管理**：底部「编辑片段数据」打开维护界面，可新增、编辑、删除片段，无需改 JSON 文件。

### 片段数据格式（底层仍为 snippets.json）

```json
[
  { "id": "1", "title": "示例：邮箱", "content": "user@example.com" },
  { "id": "2", "title": "示例：密码", "content": "your_password_here" }
]
```

- `id`：唯一字符串。 
- `title`：显示在列表中的标题，用于搜索和展示。
- `content`：实际粘贴到焦点的文本。

## 安装与运行

```bash
# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

启动后窗口会隐藏，托盘区会出现 FastType 图标；按 `Alt+Q` 调出搜索窗口。若全局快捷键无效，可尝试**以管理员身份运行**。

## 使用说明

1. 运行 FastType 后，在任意窗口（浏览器、终端、登录框等）按 `Alt+Q` 调出窗口。
2. 在搜索框输入关键字，用 ↑↓ 或鼠标选择一条结果。
3. 回车或双击该条，内容会粘贴到**调出 FastType 之前**获得焦点的输入位置。
4. 需要新增/修改片段时，点击「编辑片段数据」打开维护界面，新增、编辑或删除后关闭，再次调出 FastType 会看到更新。

## 更新日志

### v1.0.1
- **Xshell 兼容**：自动识别 Xshell 窗口，使用逐字键入方式输入内容，解决片段无法录入到 Xshell 的问题

### v1.0.0
- 初始版本：全局快捷键、搜索、粘贴、片段管理、托盘

## 注意事项

- 粘贴依赖系统级按键模拟，部分安全策略较严的输入框可能不允许，此时可改用手动复制粘贴。
- 片段数据仅保存在本机，请自行做好备份与安全（如不要将含密码的 `snippets.json` 提交到公开仓库）。
- Windows 上若全局快捷键不生效，可尝试以管理员身份运行。
