[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-orange)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
![GitHub Repo stars](https://img.shields.io/github/stars/luestr/skills?style=flat&link=https://github.com/luestr/skills)
[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=flat&logo=telegram&logoColor=white)](https://t.me/ibilibili)

| 技能名称                    | 用途                                                                                                                                                                             | 技能目录                                                    |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------- |
| lexilla                     | 使用 Lexilla 5.5.1 为 Scintilla 集成、构建、发现和扩展语言 lexer                                                                                                                 | [lexilla](/lexilla)                                         |
| scintilla                   | 将 Scintilla.dll 5.6.4 集成到 Windows 编辑器中                                                                                                                                   | [scintilla](/scintilla)                                     |
| slint                       | 使用 Slint v1.17.1 构建 GUI                                                                                                                                                      | [slint](/slint)                                             |
| write-tampermonkey-scripts  | 规划、编写、调试、测试和维护 Tampermonkey 用户脚本                                                                                                                               | [write-tampermonkey-scripts](/write-tampermonkey-scripts)   |
| write-ublock-origin-filters | 完整的 uBlock Origin (uBO) 静态过滤语法参考                                                                                                                                      | [write-ublock-origin-filters](/write-ublock-origin-filters) |
| write-adblock-plus-filters  | 编写、调试和解释 Adblock Plus (ABP) 过滤规则语法                                                                                                                                 | [write-adblock-plus-filters](/write-adblock-plus-filters)   |
| write-adguard-filters       | AdGuard 过滤规则语法                                                                                                                                                             | [write-adguard-filters](/write-adguard-filters)             |
| grit                        | 指导 Agent 如何使用 grit                                                                                                                                                         | [grit](/grit)                                               |
| answer-me-with-html         | 遇到复杂问题，让 Agent 给你绘制一页能看懂的 HTML，这是 [answer-me-with-html](https://github.com/QingYunA/answer-me-with-html/blob/main/README.zh-CN.md) 技能的 Chatlo 专项适配。 | [answer-me-with-html](/answer-me-with-html)                 |

> 注：[answer-me-with-html](/answer-me-with-html) 改编自上游 MIT 许可项目，其 SKILL.md 中声明 MIT 许可；仓库其余内容采用 CC BY-NC-SA 4.0。

## 校验

技能需满足 ZCode 的规范（`name` 与目录名一致且为小写 kebab-case、`description` 不超过 1024 字符、frontmatter 只用 `name`/`description`/`when_to_use`/`license`/`metadata`、参考文件被引用、双语文件集一致、链接有效）。修改技能后运行：

```bash
node scripts/check-skills.mjs
```
