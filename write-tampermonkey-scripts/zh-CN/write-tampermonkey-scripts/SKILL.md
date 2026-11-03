---
name: write-tampermonkey-scripts
description: 引导 AI 代理规划、编写、调试、测试和维护 Tampermonkey 用户脚本。当用户请求用户脚本、浏览器页面自动化、DOM 增强、Tampermonkey 元数据、GM_* API、@match、@grant、@run-at、@connect、跨源请求、SPA 页面集成或脚本注入任务时使用此技能，即使用户没有明确提及 Tampermonkey。
metadata:
  compatibility: 与平台无关的 Markdown 指南。请查阅 Tampermonkey 官方文档，以获取浏览器、版本、权限和 API 可用性的详细信息。
---

# Tampermonkey 用户脚本编写

使用此技能规划、编写、调试、测试和维护 Tampermonkey 用户脚本。保持指南与平台无关，并根据用户目标浏览器、页面和约束调整实现。

## 编写代码前

首先确认：

- 脚本必须运行的目标页面、URL 模式、框架以及页面上下文。
- 用户可见的行为、交互模型和成功标准。
- 页面和脚本的生命周期，包括初始加载、导航、重新加载和 teardown。
- 所需的权限、元数据、grant、注入时机和沙箱边界。
- 涉及的数据源、持久化需求、通信路径和外部服务。
- 失败模式、恢复行为，以及页面或服务发生变化时的处理方式。
- 浏览器、Tampermonkey 版本、页面结构、CSP、兼容性和无障碍约束。

使用此索引后，只阅读与任务相关的章节。在给出实现前，根据需求检查范围、grant、时机、动态页面行为、安全性和可测试性。

## 相关章节

1. [工作流](chapters/01-workflow.md)
2. [元数据](chapters/02-metadata.md)
3. [运行时权限](chapters/03-runtime-permissions.md)
4. [DOM 与样式](chapters/04-dom-and-styles.md)
5. [SPA 与动态页面](chapters/05-spa-and-dynamic-pages.md)
6. [存储与状态](chapters/06-storage-and-state.md)
7. [网络与跨源请求](chapters/07-network-and-cross-origin.md)
8. [UI 与实用 API](chapters/08-ui-and-utility-apis.md)
9. [上下文通信](chapters/09-context-communication.md)
10. [安全与隐私](chapters/10-security-and-privacy.md)
11. [调试与兼容性](chapters/11-debugging-and-compatibility.md)
12. [测试、发布与示例](chapters/12-testing-release-and-examples.md)

## 官方来源

- [Tampermonkey 文档](https://www.tampermonkey.net/documentation.php?locale=en)
- [Tampermonkey 常见问题](https://www.tampermonkey.net/faq.php?locale=en)

## 最终检查清单

- [ ] 范围和目标页面明确。
- [ ] grant 和元数据最小化且有充分理由。
- [ ] 生命周期和注入时机正确。
- [ ] 动态页面处理具备幂等性。
- [ ] 错误具有可观察且可恢复的行为。
- [ ] 已处理安全和隐私风险。
- [ ] 已说明浏览器和 Tampermonkey 兼容性。
- [ ] 已包含测试或可复现的验证流程。
