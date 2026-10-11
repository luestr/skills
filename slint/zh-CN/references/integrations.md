# Language integrations

Slint 提供 Rust、C++、JavaScript 和 Python 集成。集成层负责加载/编译 `.slint` 文件、创建 component、读写 properties、注册 callbacks、处理 models，并启动 event loop。

使用集成 API 时：让 UI 暴露稳定的 properties/callbacks；在宿主语言中维护业务状态；注意线程、生命周期、类型转换和构建工具链。

来源：[Language Integrations](https://docs.slint.dev/latest/docs/slint/language-integrations/)。