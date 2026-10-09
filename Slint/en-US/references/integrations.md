# Language integrations

Slint provides Rust, C++, JavaScript, and Python integrations. The integration layer loads or compiles `.slint` files, creates components, reads and writes properties, registers callbacks, handles models, and starts the event loop.

When using an integration API, expose stable properties and callbacks from the UI, keep application state in the host language, and account for threading, lifetimes, type conversions, and the build toolchain.

Source: [Language Integrations](https://docs.slint.dev/latest/docs/slint/language-integrations/).