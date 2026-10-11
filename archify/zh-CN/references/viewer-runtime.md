# Viewer 运行时参考 <a id="viewer-runtime-reference"></a>

仅当用户要求面向读者的能力时才读本文件。常规生成不需要实现或重新记录这些功能；它们已在生成的 HTML 中。

## 探索 <a id="exploration"></a>

- Diagram Guide 列出当前的操作与快捷键。
- Reading Depth 在默认 100% 缩放时从 READ 开始，在 175% 时揭示 FULL 细节，且只在低于 100% 时回退到 MAP。Focus、route 与语义交互在任何缩放下都揭示其确切事实。
- Semantic Lens 汇总所选的节点/关系种类，而不改变已编写的几何。
- Intent Trace 在提交聚焦之前预览一个精细指针或键盘目标。
- Node Finder 搜索标签与稳定 ID。
- Semantic Passport 在聚焦时打开，显示已编写的上游/下游事实，支持一个可复制的深层链接，有一个显式的关闭动作，在真正的外部激活与 Escape 时关闭，且绝不进入规范导出。
- Semantic Radar 镜像可见视口与已编写的图，而不会成为第二个真相来源。
- Direct Relationship Pin 使一条唯一的、经编译的关系可操作，同时保留已编写的线与稳定关系身份。它必须在来源/目标/标签/ID 元数据冲突时失败关闭。
- Route Probe 在已编写的有向关系上精确解析两个端点。它绝不从几何推断走线。

## 动效与呈现 <a id="motion-and-presentation"></a>

`meta.animation: "trace"` 启用一个有界的、由读者控制的 Live/Still 追踪。Static 是默认值。Still、减少动效、页面隐藏、打印与规范导出都保留完整的静态含义。Presentation Stage 改变查看器外壳与取景，绝不改变已编写的几何。这不是一项移动端产品功能；窄布局只获得内容收束（containment）。

## 规范导出 <a id="canonical-exports"></a>

导出菜单可以复制/下载整图 PNG、下载 JPEG/WebP、下载一个双主题 SVG，并录制一个启用追踪的 WebM。查看器状态——Guide、Lens、finder、focus、route、camera、presentation、动效归属以及临时叠加层——必须从规范导出中移除。

### Route Share Card <a id="route-share-card"></a>

在一次真实的有向 Route Probe 解析之后，读者可以使用 **Export → Route Share Card**。它复用确切的、有序的走线快照与共享的 Share Card 接缝：`format=share-card`、`variant=route`。隔离的副本只能使用静态的 `data-share-route-*` 装饰。它仅限下载，对过时/不可达/冲突的走线失败关闭，且绝不成为规范产物。

### Reach Share Card <a id="reach-share-card"></a>

在一次非空的已编写可达性查询之后，读者可以使用 **Export → Reach Share Card**。它消费已解析的上游/下游节点与边集合，而不重新运行遍历：`format=share-card`、`variant=reach`。隔离的副本只能使用静态的 `data-share-reach-*` 装饰。它仅限下载。称其为已编写的可达性——而非影响、爆炸半径、破坏或运行时因果关系。

## 真相边界 <a id="truth-boundary"></a>

查看器导出是沟通资产。它们不替代已校验的 HTML、确定性交付凭据，或一次真实的视觉审查。不要为这些仅查看器能力添加托管服务、存储面、依赖、schema 分支或移动端产品面。

## Chatlo 适配说明 <a id="chatlo-adaptation"></a>

本文件描述的是 Archify 自带 Viewer 的运行时能力。在 Chatlo 环境中，所有面向读者的浏览器操作（打开、抓取、渲染、自动化、截图、Cookie、搜索、下载等）都委派给 Chatlo 内置浏览器（WebKit/WKWebView）执行；不得安装、下载或运行任何第三方浏览器或内核。规范导出与分享卡片的实际呈现同样经由该内置浏览器完成。
