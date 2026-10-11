# 消息 API 与数据约定

## 常用消息形状

| 目的 | API | 注意 |
|---|---|---|
| 取全文 | `SCI_GETTEXT` | 分配 `length + 1`，返回文本以 NUL 结尾 |
| 设置全文 | `SCI_SETTEXT` | 传入 NUL-terminated text |
| 取行 | `SCI_GETLINE` | 使用 `SCI_LINELENGTH` 分配；返回内容不自动 NUL 结尾 |
| 替换选择 | `SCI_REPLACESEL` | 无选择时在 caret 处插入 |
| 只读 | `SCI_SETREADONLY` | 修改尝试产生 `SCN_MODIFYATTEMPTRO` |
| 保存点 | `SCI_SETSAVEPOINT` | 保存/加载完成后标记未修改 |

## 类型和内存

- 消息参数使用 pointer-sized `sptr_t`/`uptr_t`；具体 `position`、`line` 语义以消息条目为准。文本 position/text length 的 byte 或 UTF-16 code unit 规则不能一概而论；`line` 是从 0 开始的行号。
- 文档长度和范围按 byte 计，即使文本使用多字节编码；避免用字符数或 UTF-16 code unit 数直接替代。
- `const char *` 可能要求 NUL 结尾，也可能由另一个参数提供长度；逐条阅读文档。
- 对返回 `char *` 的 API，文档可能要求调用者提供足够容量；只有官方明确规定支持 `NULL` length probing 的消息才可以先传 `NULL`。
- `INVALID_POSITION` 为 `-1`。不要将无效位置继续传入范围计算。
- `colour` 是 `red | (green << 8) | (blue << 16)`；`colouralpha` 额外把 alpha 放在高字节。

## 通知

宿主通过通知结构接收修改、保存点、自动补全、焦点、鼠标 dwell、hotspot 和 zoom 事件。通知处理器中遵守各事件的重入约束；例如 hotspot 点击处理时避免修改当前 selection 或 caret，除非官方文档允许。

## 安全调用模板（C++）

```cpp
sptr_t GetText(HWND editor) {
    const sptr_t length = ::SendMessage(editor, SCI_GETTEXT, 0, 0);
    if (length < 0 || length > kMaximumDocumentBytes) {
        throw std::runtime_error("invalid document length");
    }
    std::string text(static_cast<size_t>(length) + 1, '\0');
    ::SendMessage(editor, SCI_GETTEXT, static_cast<WPARAM>(length),
                  reinterpret_cast<LPARAM>(text.data()));
    text.resize(static_cast<size_t>(length));
    return text;
}
```

实际项目中将长度上限、错误处理和线程归属替换为宿主约定；控件消息通常应在创建它的 GUI 线程调用。
