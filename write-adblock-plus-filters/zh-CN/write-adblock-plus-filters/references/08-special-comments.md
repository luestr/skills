# 特殊注释（过滤列表元数据）

过滤列表使用特殊注释（以 `!` 开头）来声明 Adblock Plus 用于列表管理的元数据。这些与普通 `!` 注释不同，普通注释仅供人类读者阅读。

## 支持的特殊注释

### `! Title: <名称>`

声明过滤列表的显示名称。

```
! Title: 我的自定义广告过滤规则
```

在 ABP 的设置界面中显示。如果省略，则使用文件名或 URL。

### `! Homepage: <URL>`

链接到过滤列表的主页或代码仓库。

```
! Homepage: https://github.com/example/filters
```

### `! Expires: <间隔>`

ABP 应多久检查一次此过滤列表的更新。

```
! Expires: 5 days
```

```
! Expires: 8 hours
```

- 有效范围：**1 小时** 到 **14 天**。
- 可以按天或小时指定。
- 实际更新时间会略微随机化以减少服务器负载 — 这是目标间隔，不是保证。

### `! Redirect: <URL>`

告诉 ABP 过滤列表已迁移到新的下载位置。

```
! Redirect: https://new-location.example.com/filters.txt
```

- ABP 会忽略此注释之后的所有内容，并立即尝试从新 URL 下载。
- 成功后，列表的 URL 会在设置中更新。
- 如果新 URL 与当前 URL 相同，这作为"规范地址"声明（用于强制列表的主 URL）。

### `! Version: <数字>`

声明过滤列表的数字版本号。

```
! Version: 2024121501
```

- 在问题报告中显示。
- 用于验证 Bug 报告是否引用了当前版本。
- 通常使用基于日期的数字（YYYYMMDDNN）或简单的递增整数。

### `! Checksum: <哈希值>`

用于验证过滤列表内容完整性的校验和值。被一些过滤列表管理工具用于检测损坏或篡改。

```
! Checksum: aBcDeFgHiJkLmNoPqRsT
```

- 通常由过滤列表编辑工具自动生成。
- 当存在时，ABP 或第三方工具可以验证列表内容未被意外修改。

## 过滤列表头部示例

```
! Title: 示例广告过滤规则
! Homepage: https://example.com/filters
! Expires: 1 day
! Version: 2024121501
! Last modified: 2024-12-15
!
! 此过滤列表拦截 example.com 及相关站点上的广告。
! 由示例团队维护。

||ads.example.com^
||example.com/ads/*
example.com##.ad-banner
```

## 最佳实践

- 始终包含 `! Title:` — 它使列表在 ABP 界面中可识别。
- 使用 `! Expires:` 控制更新频率 — 活跃维护的列表用较短间隔，稳定的列表用较长间隔。
- 使用 `! Version:` 进行追踪 — 对调试用户报告的问题非常有价值。
- `! Redirect:` 在将列表迁移到新主机时至关重要 — 旧订阅者会无缝跟随重定向。
- 将特殊注释放在文件顶部，在所有过滤规则之前。
