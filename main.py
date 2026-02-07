# -*- coding: utf-8 -*-
"""
QuickType - 快捷键调出，搜索常用文本后回车粘贴到当前焦点。
Python + PyQt5 方案，可直接向系统发送按键，无沙箱限制。
"""
import json
import os
import re
import subprocess
import sys
import ctypes
from pathlib import Path

import keyboard
import pyperclip

# Windows: 保存/恢复“按快捷键前获得焦点的窗口”，以便粘贴到浏览器/IDE
if sys.platform == "win32":
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    HWND_TOPMOST = -1
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001

    def get_foreground_hwnd():
        return user32.GetForegroundWindow()

    def set_foreground_hwnd(hwnd):
        if hwnd and user32.IsWindow(hwnd):
            user32.SetForegroundWindow(hwnd)

    def _set_window_topmost(widget, on_top=True):
        """把窗口设为“置顶”或取消，确保弹框显示在最前。"""
        hwnd = int(widget.winId())
        insert_after = HWND_TOPMOST if on_top else -2  # -2 = HWND_NOTOPMOST
        user32.SetWindowPos(hwnd, insert_after, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)

    def _force_our_window_foreground(widget):
        """用 AttachThreadInput 抢前台，解决首次弹出时焦点仍在 IDE 的问题。"""
        our_hwnd = int(widget.winId())
        fg_hwnd = user32.GetForegroundWindow()
        if not fg_hwnd or fg_hwnd == our_hwnd:
            user32.SetForegroundWindow(our_hwnd)
            return
        fg_tid = user32.GetWindowThreadProcessId(fg_hwnd, None)
        our_tid = kernel32.GetCurrentThreadId()
        if user32.AttachThreadInput(our_tid, fg_tid, True):
            try:
                user32.SetForegroundWindow(our_hwnd)
            finally:
                user32.AttachThreadInput(our_tid, fg_tid, False)
        else:
            user32.SetForegroundWindow(our_hwnd)
else:
    def get_foreground_hwnd():
        return None

    def set_foreground_hwnd(hwnd):
        pass

    def _set_window_topmost(widget, on_top=True):
        pass

    def _force_our_window_foreground(widget):
        pass

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QAbstractItemView,
    QSystemTrayIcon,
    QMenu,
    QAction,
    QStyle,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPlainTextEdit,
    QFormLayout,
    QMessageBox,
    QDialogButtonBox,
)

SNIPPETS_FILE = "snippets.json"
HOTKEY = "alt+q"
# Logo 放这里：项目根目录下 build/icon.ico（或 build/icon.png）
# 打包后 PyInstaller 解压到 sys._MEIPASS，图标从该目录读
_APP_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
ICON_PATHS = [
    os.path.join(_APP_DIR, "build", "icon.ico"),
    os.path.join(_APP_DIR, "build", "icon.png"),
]


def _app_icon():
    """若有 build/icon.ico 或 build/icon.png 则返回 QIcon，否则 None。"""
    for p in ICON_PATHS:
        if os.path.isfile(p):
            return QIcon(p)
    return None
PASTE_DELAY_MS = 80
PASTE_DELAY_AFTER_FOCUS_MS = 180
# 发送 Ctrl+V 后等目标应用读完剪贴板再恢复，否则会贴成旧内容
PASTE_DELAY_BEFORE_RESTORE_CLIP_MS = 250
# 首次弹出后多次尝试把焦点放到搜索框
FOCUS_SEARCH_DELAYS_MS = (50, 120, 220)


def get_snippets_path() -> str:
    base = os.path.join(os.path.expanduser("~"), ".quicktype")
    Path(base).mkdir(parents=True, exist_ok=True)
    return os.path.join(base, SNIPPETS_FILE)


def load_snippets() -> list:
    path = get_snippets_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return get_default_snippets()


def save_snippets(snippets: list) -> None:
    path = get_snippets_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snippets, f, ensure_ascii=False, indent=2)


def get_default_snippets() -> list:
    return [
        {"id": "1", "title": "示例：邮箱", "content": "user@example.com"},
        {"id": "2", "title": "示例：密码占位", "content": "your_password_here"},
    ]


def filter_snippets(snippets: list, keyword: str) -> list:
    if not keyword or not keyword.strip():
        return snippets
    pattern = re.escape(keyword.strip())
    try:
        r = re.compile(pattern, re.I)
    except re.error:
        return snippets
    return [s for s in snippets if r.search(s.get("title", "")) or r.search(s.get("content", ""))]


def open_snippets_file() -> None:
    path = get_snippets_path()
    if not os.path.isfile(path):
        save_snippets(get_default_snippets())
    if sys.platform == "win32":
        os.startfile(path)
    else:
        subprocess.run(["xdg-open", path], check=False)


def _next_snippet_id(snippets: list) -> str:
    """生成新片段的 id。"""
    nums = []
    for s in snippets:
        try:
            nums.append(int(s.get("id", 0)))
        except (TypeError, ValueError):
            pass
    return str(max(nums, default=0) + 1)


class SnippetEditDialog(QDialog):
    """新增/编辑单条片段的对话框。"""

    def __init__(self, parent=None, snippet=None):
        super().__init__(parent)
        self.setWindowTitle("编辑片段" if snippet else "新增片段")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("标题（用于搜索和列表显示）")
        layout.addRow("标题：", self.title_edit)
        self.content_edit = QPlainTextEdit()
        self.content_edit.setPlaceholderText("内容（粘贴到焦点时的文本，可多行）")
        self.content_edit.setMinimumHeight(120)
        layout.addRow("内容：", self.content_edit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)
        if snippet:
            self.title_edit.setText(snippet.get("title", ""))
            self.content_edit.setPlainText(snippet.get("content", ""))

    def get_data(self):
        return {
            "title": self.title_edit.text().strip(),
            "content": self.content_edit.toPlainText(),
        }


class SnippetsMaintenanceDialog(QDialog):
    """片段维护界面：列表 + 新增/编辑/删除。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("维护片段数据")
        self.setMinimumSize(640, 400)
        self._snippets = []
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["标题", "内容预览", "id"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self._on_edit)
        layout.addWidget(self.table)
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("新增")
        add_btn.clicked.connect(self._on_add)
        edit_btn = QPushButton("编辑")
        edit_btn.clicked.connect(self._on_edit)
        del_btn = QPushButton("删除")
        del_btn.clicked.connect(self._on_delete)
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        self._load_table()

    def _load_table(self):
        self._snippets = load_snippets()
        self.table.setRowCount(len(self._snippets))
        for i, s in enumerate(self._snippets):
            self.table.setItem(i, 0, QTableWidgetItem(s.get("title", "")))
            content = s.get("content", "")
            preview = (content[:80] + "…") if len(content) > 80 else content
            self.table.setItem(i, 1, QTableWidgetItem(preview))
            self.table.setItem(i, 2, QTableWidgetItem(s.get("id", "")))

    def _on_add(self):
        dlg = SnippetEditDialog(self, snippet=None)
        if dlg.exec_() != QDialog.Accepted:
            return
        data = dlg.get_data()
        if not data["title"] and not data["content"]:
            return
        new_id = _next_snippet_id(self._snippets)
        self._snippets.append({
            "id": new_id,
            "title": data["title"] or "（无标题）",
            "content": data["content"],
        })
        save_snippets(self._snippets)
        self._load_table()

    def _on_edit(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._snippets):
            QMessageBox.information(self, "提示", "请先选中一条片段。")
            return
        snippet = self._snippets[row]
        dlg = SnippetEditDialog(self, snippet=snippet)
        if dlg.exec_() != QDialog.Accepted:
            return
        data = dlg.get_data()
        snippet["title"] = data["title"] or "（无标题）"
        snippet["content"] = data["content"]
        save_snippets(self._snippets)
        self._load_table()

    def _on_delete(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._snippets):
            QMessageBox.information(self, "提示", "请先选中一条片段。")
            return
        title = self._snippets[row].get("title", "")
        if QMessageBox.question(
            self, "确认删除",
            f"确定要删除「{title}」吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        ) != QMessageBox.Yes:
            return
        self._snippets.pop(row)
        save_snippets(self._snippets)
        self._load_table()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.snippets = []
        self.filtered = []
        self.selected_index = 0
        self._setup_ui()
        self._load_snippets()

    def _setup_ui(self):
        self.setWindowTitle("QuickType")
        self.setFixedSize(700, 480)
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint
        )
        icon = _app_icon()
        if icon is not None:
            self.setWindowIcon(icon)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 搜索框
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键字搜索...")
        self.search_edit.setStyleSheet("""
            QLineEdit { padding: 8px 10px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px; }
            QLineEdit:focus { border-color: #0078d4; }
        """)
        self.search_edit.textChanged.connect(self._on_search_changed)
        self.search_edit.returnPressed.connect(self._on_enter)
        layout.addWidget(self.search_edit)

        # 结果列表
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(False)
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.list_widget.setFocusPolicy(Qt.StrongFocus)
        self.list_widget.itemDoubleClicked.connect(self._on_item_activated)
        self.list_widget.currentRowChanged.connect(self._on_row_changed)
        self.list_widget.setStyleSheet("""
            QListWidget { border: none; outline: none; }
            QListWidget::item {
                padding: 8px 10px;
                min-height: 1.2em;
                color: #333;
            }
            QListWidget::item:selected, QListWidget::item:hover {
                background: #b8daff;
                color: #111;
            }
        """)
        layout.addWidget(self.list_widget)

        # 状态栏
        status = QHBoxLayout()
        self.status_label = QLabel("0 条")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        open_btn = QPushButton("编辑片段数据")
        open_btn.setFlat(True)
        open_btn.setStyleSheet("color: #0078d4; font-size: 12px; border: none;")
        open_btn.clicked.connect(self._open_snippets_file)
        status.addWidget(self.status_label)
        status.addStretch()
        status.addWidget(open_btn)
        status_widget = QWidget()
        status_widget.setLayout(status)
        status_widget.setStyleSheet("background: #f5f5f5; padding: 4px 10px; border-top: 1px solid #e0e0e0;")
        layout.addWidget(status_widget)

        self.list_widget.installEventFilter(self)
        self.search_edit.installEventFilter(self)

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent
        if obj == self.search_edit and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Down, Qt.Key_Up):
                self.list_widget.setFocus()
                self._move_selection(1 if event.key() == Qt.Key_Down else -1)
                return True
        if obj == self.list_widget:
            from PyQt5.QtCore import QEvent
            if event.type() == QEvent.KeyPress:
                key = event.key()
                if key == Qt.Key_Return or key == Qt.Key_Enter:
                    self._paste_current()
                    return True
                if key == Qt.Key_Up:
                    self._move_selection(-1)
                    return True
                if key == Qt.Key_Down:
                    self._move_selection(1)
                    return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
            return
        if event.key() in (Qt.Key_Up, Qt.Key_Down):
            self.list_widget.setFocus()
            self.list_widget.keyPressEvent(event)
            return
        super().keyPressEvent(event)

    def _load_snippets(self):
        self.snippets = load_snippets()
        self._apply_filter()

    def _on_search_changed(self, text):
        self._apply_filter()

    def _apply_filter(self):
        keyword = self.search_edit.text().strip()
        self.filtered = filter_snippets(self.snippets, keyword)
        self.selected_index = min(self.selected_index, max(0, len(self.filtered) - 1))
        self._refresh_list()
        self.status_label.setText(f"{len(self.filtered)} 条")

    def _refresh_list(self):
        self.list_widget.clear()
        for i, s in enumerate(self.filtered):
            title = s.get("title", "")
            content = s.get("content", "")
            preview = (content[:60] + "…") if len(content) > 60 else content
            item = QListWidgetItem(f"  {title}    {preview}")
            item.setData(Qt.UserRole, content)
            self.list_widget.addItem(item)
        if self.filtered:
            self.list_widget.setCurrentRow(self.selected_index)
            self.list_widget.scrollTo(self.list_widget.currentIndex())

    def _on_row_changed(self, row):
        if 0 <= row < len(self.filtered):
            self.selected_index = row

    def _move_selection(self, delta):
        n = len(self.filtered)
        if n == 0:
            return
        self.selected_index = (self.selected_index + delta) % n
        self.list_widget.setCurrentRow(self.selected_index)
        self.list_widget.scrollTo(self.list_widget.currentIndex())

    def _on_enter(self):
        self._paste_current()

    def _on_item_activated(self, item):
        content = item.data(Qt.UserRole)
        if content:
            self._paste_to_focus(content)

    def _paste_current(self):
        if 0 <= self.selected_index < len(self.filtered):
            content = self.filtered[self.selected_index].get("content", "")
            if content:
                self._paste_to_focus(content)

    def _paste_to_focus(self, text: str):
        """隐藏窗口后先恢复“按快捷键前的窗口”焦点，再发送 Ctrl+V，并恢复原剪贴板。"""
        try:
            old_clip = pyperclip.paste()
        except Exception:
            old_clip = ""
        pyperclip.copy(text)
        restore_hwnd = getattr(self, "_prev_foreground_hwnd", None)
        self.hide()
        QTimer.singleShot(
            PASTE_DELAY_MS,
            lambda: self._do_send_paste(old_clip, restore_hwnd),
        )

    def _do_send_paste(self, restore_clip: str, restore_hwnd=None):
        if sys.platform == "win32" and restore_hwnd is not None:
            set_foreground_hwnd(restore_hwnd)
            QTimer.singleShot(
                PASTE_DELAY_AFTER_FOCUS_MS,
                lambda: self._send_ctrl_v_and_restore_clip(restore_clip),
            )
        else:
            self._send_ctrl_v_and_restore_clip(restore_clip)

    def _send_ctrl_v_and_restore_clip(self, restore_clip: str):
        try:
            keyboard.press_and_release("ctrl+v")
        except Exception:
            pass
        # 等目标应用读完剪贴板再恢复，否则会贴成旧内容
        QTimer.singleShot(
            PASTE_DELAY_BEFORE_RESTORE_CLIP_MS,
            lambda: self._restore_clipboard(restore_clip),
        )

    def _restore_clipboard(self, restore_clip: str):
        try:
            pyperclip.copy(restore_clip)
        except Exception:
            pass

    def _open_snippets_file(self):
        dlg = SnippetsMaintenanceDialog(self)
        dlg.exec_()
        self._load_snippets()

    def _on_hotkey_show(self):
        """由快捷键触发，在主线程里取前台窗口再显示，避免在键盘线程里调 Win32。"""
        try:
            prev_hwnd = get_foreground_hwnd() if sys.platform == "win32" else None
        except Exception:
            prev_hwnd = None
        self.show_and_focus(prev_hwnd)

    def show_and_focus(self, prev_foreground_hwnd=None):
        if prev_foreground_hwnd is not None:
            self._prev_foreground_hwnd = prev_foreground_hwnd
        self._load_snippets()
        self.search_edit.clear()
        self.selected_index = 0
        self._apply_filter()
        self.show()
        if sys.platform == "win32":
            try:
                _set_window_topmost(self, True)
            except Exception:
                pass
        self.raise_()
        self.activateWindow()
        if sys.platform == "win32":
            try:
                _force_our_window_foreground(self)
            except Exception:
                pass
        self.search_edit.setFocus()
        for delay_ms in FOCUS_SEARCH_DELAYS_MS:
            QTimer.singleShot(delay_ms, self._focus_search_again)

    def _focus_search_again(self):
        if self.isVisible():
            self.raise_()
            self.activateWindow()
            self.search_edit.setFocus()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("QuickType")
    window = MainWindow()

    tray = QSystemTrayIcon(parent=window)
    if tray.isSystemTrayAvailable():
        icon = _app_icon()
        if icon is not None:
            tray.setIcon(icon)
        else:
            tray.setIcon(app.style().standardIcon(QStyle.SP_ComputerIcon))
        menu = QMenu()
        show_act = QAction("显示 QuickType", menu)
        show_act.triggered.connect(window.show_and_focus)
        menu.addAction(show_act)
        quit_act = QAction("退出", menu)
        quit_act.triggered.connect(app.quit)
        menu.addAction(quit_act)
        tray.setContextMenu(menu)
        tray.activated.connect(
            lambda reason: window.show_and_focus() if reason == QSystemTrayIcon.DoubleClick else None
        )
        tray.show()
    else:
        window.show_and_focus()

    def on_hotkey():
        QTimer.singleShot(0, window._on_hotkey_show)

    try:
        keyboard.add_hotkey(HOTKEY, on_hotkey, suppress=False)
    except Exception as e:
        print("全局快捷键注册失败（可能需要管理员权限）:", e)
        print("请以管理员身份运行，或修改 HOTKEY 后重试。")

    window.hide()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
