# 讲解视频（am video，3Blue1Brown 风格）

当 SKILL.md 第 7 节把你送到这里时读本文。`am` 指 SKILL.md 第 2 节那条完整命令（含 `AM_HOME=/agent/outputs/answer-me-with-html`）；本文件里出现的脚本路径请按本文件所在目录解析为绝对路径（安装后本目录为 `/agent/skills/answer-me-with-html/zh-CN/`）。

视频草稿与页面草稿格式相同，只多一条规则：以 `>` 开头的行是旁白，一行一拍。

````bash
AM_HOME=/agent/outputs/answer-me-with-html bun scripts/am.mjs video - --no-open <<'AM_EOF'
---
title: TCP 三次握手
subtitle: 为什么是三次
---
> 开场旁白（可选）。

## 两端在等待
```sequence
Client -> Server: SYN
Server -> Client: SYN-ACK
Client -> Server: ACK
```
> 客户端先发 SYN，请求建立连接。
> [Server] 用 SYN-ACK 回应。
> 客户端再回 ACK，连接建立。
AM_EOF
````

- 一个 `## ` 是一个场景。每个场景放一个组件（或一个表格、一个列表）当画面，下面写 2–5 行旁白。
- 第 N 行旁白播放时，画面显示第 N 步。flow / er / sequence / tree 里源文件每行是一步；timeline、limits、表格行、列表项按条目步进。因此组件的行顺序就是讲解顺序。旁白行多于步数时，多出来的开头几行当作开场，不显示新内容。
- 旁白里写 `[名称]`：镜头会拉近并高亮该名称的节点或角色，名称要与组件里写法一致。
- 相邻场景同名的节点会平滑移动到新位置。想让观众跟随同一对象，就在下一场景复用同名。
- 每个视频 3–6 个场景，每行旁白一两句。
- 旁白是要朗读出来的，所以按口语写，像面对面讲解：`你看`、`那问题来了`、`我们换个角度看` 这类转折没问题，人物"台词"用引号。不要写成说明书。句子长度仍受 STE 检查。
- 外观默认跟随设置里的主题（通常是 blueprint 制图风格）。想要"那种深色 3b1b 风格"，在 frontmatter 写 `theme: 3b1b`。

## Chatlo 专属：朗读与视频导出

### 朗读（`--voice`）

- 默认 `--voice auto`：有 `ELEVENLABS_API_KEY` 就用 ElevenLabs，否则用系统 TTS，两者都没有就只留字幕。
- **Chatlo 没有 macOS 的 `say`，也没有 `espeak-ng`**，所以默认结果是**只有字幕、无配音**。想要配音，任选其一：
  - 设 `ELEVENLABS_API_KEY`（配 `--voice elevenlabs`，或直接 auto）；
  - 设 `AM_TTS_URL` 指向本机 OpenAI 兼容语音服务，并用 `--voice local`。
- 用户说"不要声音"时加 `--voice off`（在 Chatlo 上等同于默认）。

### 输出

- `am video` 产出**单文件播放器页**，落在 `AM_HOME/videos/` 下。播放器带章节条（跳到某场景）、倍速按钮（0.5×–2×）和导出按钮（⤓）。

### 导出视频文件（重点，Chatlo 专用）

- 上游的 `am video --mp4`（本地 Chrome + CDP，再用 ffmpeg 编 H.264）与 `--webm`（本地 Chrome + CDP 驱动页内编码器）**在 Chatlo 都不可用**：Chatlo 不允许安装任何第三方浏览器，也没有可用的 Chrome 通道。**不要**使用这两个开关。
- Chatlo 上导出**只能**用内置浏览器里的 WebCodecs 编码器，容器为 **WebM，视频编码仅 VP8 / VP9**（本机实测支持 VP9 `vp09.00.31.08`、VP8，以及 Opus 音频）。用本技能自带脚本：

```bash
AM_HOME=/agent/outputs/answer-me-with-html bun scripts/chatlo-export.mjs \
  "/agent/outputs/answer-me-with-html/videos/<播放器页>.html" \
  "/agent/outputs/answer-me-with-html/videos/<输出>.webm" --bitrate 900000
```

- 该脚本用 `chatlo-browser` 在内置浏览器（WebKit）里打开播放器页，驱动页内编码器（`window.__amvEnc`）逐帧编码，再把字节写回本地 `.webm`。它**不会**调用 Chrome、CDP、Playwright 或 Puppeteer。
- 导出后用 `ffprobe` 校验（本机有 `ffprobe`）：`ffprobe -v error -show_entries stream=codec_name,width,height -of default=noprint_wrappers=1 <文件>`，应显示 `codec_name=vp9`（或 `vp8`）。
- 播放器页自带的导出按钮（⤓）也能在 Chatlo 内置浏览器里直接导出 WebM；需要文件落到本地时优先用上面的脚本。
- 若用户明确要 **MP4**：Chatlo 上不可用（无本地 Chrome，且内置浏览器 WebCodecs 只导 WebM）。可先用上面的脚本导出 WebM，再用本机 `ffmpeg` 转换：`ffmpeg -i in.webm out.mp4`，并向用户说明这是转码，而非上游的原生 MP4 路径。
- 完整语法：`am help video`。终端里用一句结论 + 播放器页链接（以及视频文件链接）回复。
