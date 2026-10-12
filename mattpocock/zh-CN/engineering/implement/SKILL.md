---
name: implement
description: "实现规格说明或工单中描述的一项工作。"
disable-model-invocation: true
---

实现用户在规格说明或工单中描述的工作。

如果用户传入一个工单引用，先从 issue 跟踪器取回它，并在开始前说明它的标题。如果引用有歧义，就询问。

尽可能在预先商定的接缝处用 “tdd” 调用 Skill 工具。

定期跑类型检查，定期跑单个测试文件，最后完整跑一次整个测试套件。

完成后，用 “code-review” 调用 Skill 工具来评审这项工作。

把工作提交到当前分支。
