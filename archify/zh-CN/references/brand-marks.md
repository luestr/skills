# 品牌标识 <a id="brand-marks"></a>

仅当某个真实的产品、provider、模型家族、渠道或服务身份有助于读者时，才使用品牌标识。语义 `type` 仍解释该节点做什么；`brand` 解释它是谁的产品。

## Agent 决策路径 <a id="agent-decision-path"></a>

1. 当请求命名了一个可识别的品牌时，搜索内置目录：

   ```bash
   bun bin/archify.mjs brands "Claude" --json
   ```

2. 把返回的规范 ID 放进节点、参与者或状态：

   ```json
   {
     "id": "planner",
     "type": "backend",
     "label": "Claude",
     "brand": "claude"
   }
   ```

3. 若目录中没有匹配项，而用户提供了官方网站，则显式捕获其图标：

   ```bash
   bun bin/archify.mjs brands capture "https://partner.example.com" --json
   ```

   把该命令的、由摘要（digest）固定的 `brand` 值放进编写的节点里：

   ```json
   {
     "id": "partner",
     "type": "external",
     "label": "Partner portal",
     "brand": {
       "url": "https://partner.example.com",
       "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
     }
   }
   ```

4. 若既无匹配项也无用户提供的 URL，则省略 `brand`。不要编造 URL，也不要悄悄指派一家视觉上相似的公司。

已知品牌的 URL 解析为内置矢量资源，而不走网络。对于发现的图标 `href` 属性，捕获会在 URL 解析之前先解码基本具名引用 `amp`、`quot`、`apos`、`lt`、`gt`（及其已定义的大写别名），以及十进制和十六进制数字引用，仅解码一次。因此 `/icon.png?v=1&amp;size=32` 会请求 `/icon.png?v=1&size=32`。URL 百分号转义保持原样；嵌套转义不会被递归解码。这个有界解码器不会添加一个通用 HTML 解析器，也不支持每一个具名 HTML 实体。HTML 读取会在不在注释内的显式 head 结束处、raw-text 元素和带引号属性处停止，包括这些标记跨越网络分块时。256 KiB 的 head 上限与捕获截止时间仍然适用；head 之后更大的 body 不会为发现图标而读取。
未知 URL 的捕获只接受有界的栅格图像格式，阻止凭据、非标准公共端口以及私有或链路本地目的地，使用有界并发与一个总的截止时间，并返回捕获内容摘要。其后的 render 与 validate 操作要求这个确切的摘要；被阻止、不可用、已更改、过大或不安全的内容会失败关闭（fail closed），而不是悄悄改变该产物。

页面、图标与重定向请求发送 `Accept-Encoding: identity`。捕获不压缩响应体：一个声明了其他内容编码的成功响应会显式关闭并拒绝。这让现有的字节上限与固定摘要与未编码表示保持一致。稍后仍可能有一个可用图标成功；否则会保留一个编码错误，而不是被一个无关的 favicon 404 掩盖。

最终产物在被打开时绝不获取品牌资产。预设矢量与经摘要校验的已捕获站点图标仍会嵌入 SVG、PNG、WebP、JPEG、Share Card 与 WebM 导出中。

使用 `bun bin/archify.mjs brands --json` 来检视所有规范 ID、别名、类别、域名与出处。当前类别涵盖 AI、cloud、engineering、data、collaboration、business systems、channels、languages 与 frameworks。
