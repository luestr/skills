# archify（Chatlo 适配版）

把任何想法、计划或代码库转化为精美的交互式图表。改编自 [tt-a1i/archify](https://github.com/tt-a1i/archify)（MIT），按 Chatlo 环境（iOS，内置 WebKit 浏览器）专项适配。

| 语言 | 目录 | 技能名 | 元数据 |
|---|---|---|---|
| 简体中文（主开发语言） | [`zh-CN/archify/`](zh-CN/archify/) | `archify` | `metadata.language: zh-CN` |
| American English | [`en-US/archify/`](en-US/archify/) | `archify` | `metadata.language: en-US` |

两个版本使用同一个技能名，功能与行为保持一致。**只安装你需要的那个**——每个目录都是自足的，互不引用。

## 安装

把语言目录下的 `archify/` 整个放进你的 agent 的技能目录。运行时统一使用 `bun`；涉及浏览器的步骤只用 Chatlo 内置浏览器。

## 许可

MIT，见 [`LICENSE`](LICENSE)。

技能内含可选的第三方品牌图标矢量数据，其各自的许可与商标条款见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。这两份文件都放在仓库层而非技能目录内——它们不参与技能运行，放进技能目录只会混进安装包。
