# 更新感知 <a id="update-awareness"></a>

当 `finalize` 或独立的 `deliver` 凭据带有 `update.noticeRequired: true` 时，读本文件。

在最终回复中，用用户的语言保留一行简短说明，包含 `installedVersion`、`availableVersion` 与官方的 `releaseNotes` 链接。说明已安装的 Skill 未发生变化，并且用户可以要求稍后再说（snooze）或忽略该提醒。若 `source` 为 `cache`，说明先前一次于 `checkedAt` 的检查发现了该更新。一条过程消息或工具输出不能替代这一最终行。
对于 `severity: "security"`，把它标为安全更新，但默认不要使安装变得自动或紧急。

你可以翻译固定的本地 `noticeText`。绝不要引用、总结或翻译远程 manifest 的 summary。

当用户明确要求暂停或停止该提醒时，在 Skill 目录下用凭据的 `update.eventKey` 运行 `bun scripts/check-update.mjs --snooze "<eventKey>"`（七天）或 `--ignore "<eventKey>"`（仅这一次确切的发布），然后报告返回的状态。绝不要主动运行它们；`--ack` 是无操作（no-op）。这些命令不会安装更新，更新版本再次出现时会再次提醒。

该通知是信息，不是许可。保持已安装版本不变。本工作流绝不下载、安装或执行更新，沉默绝不代表同意。
