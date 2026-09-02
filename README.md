<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License">
</p>

# 字幕遮挡器 / Subtitle Blocker

看外语视频时，字幕经常是**双语**的：上面一行中文、下面一行目标语言。它帮你**只遮住中文那行**，让下面那行目标语言字幕露出来，方便二语学习者沉浸式看片。

Who is this for? 看美剧/电影时想摆脱中文字幕、只留外语字幕的二语学习者。

---

## 这个工具是什么 / What it does

- 一个**置顶的不透明彩色长条**，浮在所有窗口之上，盖住中文字幕行。
- 挡条默认**透鼠标**：点在条上会穿给下面的播放器，不影响你点播放/全屏/拉进度。
- 挡条**右端内侧有两个小按钮**：
  - **[✎ 编辑]**：进入编辑模式——拖动主体移动、拖四角/边缘缩放；按钮变成 **[✓]**，点它锁定（`Esc` 也行）。
  - **[✕ 关闭]**：隐藏挡条。
- 托盘图标（右下角）里保留全部功能：显示/隐藏、恢复默认位置、编辑、颜色/透明度、语言切换、退出。
- 从托盘改**颜色/透明度/位置**时，如果挡条是隐藏的，会**先自动显示**，方便实时预览。
- **记住**位置/长宽/颜色/透明度，下次打开不变。

> 它不做 OCR、不做自动识别字，就是一个**手动的遮挡条**。首次打开停在你屏幕底部约 12% 高的地方（对准上排中文字幕的常见位置），你再用编辑模式微调即可。

It is NOT an OCR tool. It is a simple manual overlay bar: drag it to cover the Chinese line, leave the target-language line visible.

---

## 显隐方式 / Show & hide

1. **双击 exe**：启动并显示挡条；运行中再双击一次会把挡条**显示**出来（不会隐藏、不会开第二个）。
2. 挡条上的 **[✕]** 按钮：隐藏挡条。
3. 点**托盘图标**（左键切换显隐）。

---

## 安装与运行 / Run it

### 从源码运行 (From source)

需要 Python 3.10+。

```bash
pip install -r requirements.txt
python main.py
```

### macOS 说明

- macOS 的“原生全屏”视频会把视频放进独立空间，普通悬浮窗可能盖不上去——请使用**窗口模式 / 无边框全屏**。

### 打包成独立程序 / Package

```bash
pip install pyinstaller
# Windows
pyinstaller --onefile --noconsole --name SubtitleBlocker main.py
# macOS
pyinstaller --windowed --name SubtitleBlocker main.py
```

发布时推送 `v*` 标签即可触发 `.github/workflows/build.yml`，自动在 GitHub Releases 附上 Windows exe 和 macOS app（未签名，系统会提示“未知来源”，请选择运行/右键打开）。

---

## 使用 / Usage

1. 打开视频（窗口模式或浏览器全屏），双击 exe 让挡条出现。
2. 挡条默认停在底部上排中文字幕的位置；点挡条右端的 **[✎]** 进入编辑模式。
3. 拖动移动、拖四角/边缘缩放，遮住中文那行、露出下面外语行。
4. 点 **[✓]**（或按 `Esc`）锁定；点 **[✕]** 隐藏。下次打开会记住这个位置。

右键托盘图标可以：显示/隐藏、恢复默认位置、进入编辑、改颜色/透明度、切换语言、退出。

---

## 已知局限 / Known limitations

- **“独占全屏”的少数播放器**（真·硬件覆盖层）会把图像渲染在普通置顶窗口之上，挡条可能被盖住。请改用窗口或无边框全屏模式。
- 挡条是静态的，不会跟踪移动的字幕；换清晰度或挪动播放器窗口后需手动微调。

---

## 参与 / Contributing

欢迎提 issue 和 PR。代码结构：

- `main.py` — 入口（含单实例保护）
- `app/bar_window.py` — 挡条窗口（绘制、点击穿透、拖动、缩放、编辑模式）
- `app/bar_buttons.py` — 挡条内的编辑/关闭小按钮
- `app/controller.py` — 托盘、状态协调
- `app/host.py` — 单实例消息窗口
- `app/i18n.py` — 中文 / English 文案
- `app/config.py`、`app/defaults.py` — 配置与默认位置

---

## License

[MIT](LICENSE)
