# LX04 人工智能语音助手部署

把小米小爱触屏音箱 LX04 改造成 Nabu 语音助手。说「小爱同学」唤醒，接下来可以连续对话，也可以在它说话时插话。家里有多台小爱时，沿用原厂就近唤醒；有 Home Assistant（HA）时，还可以用语音查状态、控灯。

## 第一次用？把这段发给你的 Agent

把本项目链接发给能读 GitHub 的 Agent 就可以开始。想直接说明「我要部署」，也可以复制下面整段发给 Codex、Claude Code、Cursor 中的 Agent 或聊天助手。音箱系统和服务配置都可以回答「不确定」。

```text
我刚拿到一台小米 LX04，请按这个项目帮我把它部署成语音助手：
https://github.com/huacao59109/deploy-nabu-lx04

请先读 SKILL.md 和 references/preflight.md，再用一轮简短的问题问清我的设备、电脑、网络、已有服务和想做的事。不知道的项目我会说“不确定”，请帮我判断。根据我的回答推荐一个档位，说清还缺什么、是否需要刷机，然后带我完成部署和验收。能在我电脑上执行的步骤请代我做；需要我动手时，告诉我当前这一步怎么做。密钥由我在设备或后台输入。刷机会覆盖数据，写入前请单独向我确认。
```

**给只收到项目链接的 Agent**：请先读[部署入口](SKILL.md)和[配置问诊](references/preflight.md)。把用途确认和配置问题放在同一条回复里，让想部署的人可以一次答完。可以这样开场：

> 这是让小爱触屏音箱支持连续对话和插话的项目。你想先了解，还是准备部署？如果准备部署，请顺手告诉我三件事：
>
> 1. 音箱底标是什么型号、系统是否已刷 SP5.5？手边有 Windows 电脑吗？
> 2. 主要想聊天、做复杂推理，还是控制家电？家里有 Home Assistant 吗？
> 3. 已开通过哪些语音 API，或已有 Hermes 等网关？音箱能连 Wi-Fi 上网吗？
>
> 不确定就写「不确定」，不用发密钥。等你回复，我再推荐档位。

用户已给出的信息直接沿用。收到回答后给出一个推荐、理由和下一步，带用户按结果继续，直到完成唤醒、插话和所选功能的验收。

**Agent 打不开 GitHub 时**，可以[下载轻量部署包](https://github.com/huacao59109/deploy-nabu-lx04/releases/latest/download/deploy-nabu-lx04-lite.zip)并完整解压，让它打开 `deploy-nabu-lx04` 文件夹。聊天助手可以先读你上传的 `SKILL.md` 和 `references/preflight.md` 两个文件完成选档，再按需读取安装或刷机说明。具有本机终端和设备访问权限的 Agent 可以代为执行；仅能聊天的助手可以逐步给出 Windows 操作，根据你反馈的结果继续。

## Agent 会怎么帮你选档？

| 档位 | 适合的配置 | 家庭设备控制 |
|---|---|---|
| 标准 | Hermes 网关＋OpenAI Realtime，使用已启用 GPT-Live 的 profile | 由同一 Hermes profile 接入 HA、执行任务 |
| 中配 | 豆包 Seeduplex 语音，启用 Seed Pro 复杂推理时另配方舟 Key 和模型 ID | LX04 可直接发现并接入 HA |
| 低配 | 一个已开通 Seeduplex 的豆包语音 Key，用于日常对话和控灯 | LX04 可直接发现 HA，确认地址后填写 HA 令牌 |

例如，你只有一个豆包 Seeduplex 语音 Key，家里有 HA，主要想聊天、关灯，就选**低配＋HA**。不清楚 HA 地址也可以先选档，稍后让 LX04 查找；确认实例后再填写 HA 令牌。

同一个部署包已包含三档通用的签名 APK。已经运行 SP5.5 的音箱直接进入[安装与验收](references/deployment.md)。原厂或系统未知的设备先核对底标和系统，确需刷机时再按[SP5.5 刷机说明](references/flashing.md)下载并校验材料。最后靠近音箱说「小爱同学」，实测它能否接话、在播报时让你插话，并完成所选档位的任务。

## 分发与许可

本仓库公开部署 skill、文档和辅助脚本。Nabu LX04 应用以签名 APK 交付，应用自有源码由开发者私有维护。上游 MIT 代码附有[许可文本](assets/UPSTREAM-MIT.txt)。APK 内的 Emotion Ball 引擎和角色视觉分别适用随附的 LICENSE 和 NOTICE，其中球形角色视觉仅供个人技术学习和研究使用。
