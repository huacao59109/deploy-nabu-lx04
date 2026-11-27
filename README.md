# LX04 人工智能语音助手部署

这个 Codex skill 帮你把小米小爱触屏音箱 LX04 配成可连续对话、可插话的 Nabu 语音助手。音箱通过原生「小爱同学」唤醒，多台小爱共存时沿用原厂就近唤醒。

## 从这里开始

1. [下载轻量部署包](https://github.com/huacao59109/deploy-nabu-lx04/releases/latest/download/deploy-nabu-lx04-lite.zip)，在 Windows 上完整解压。ZIP 已包含签名的 Nabu LX04 APK。
2. 在 Codex 中打开解压后的 `deploy-nabu-lx04` 文件夹，告诉它「按这里的 SKILL.md 帮我配置刚拿到的 LX04」。可以直接说明音箱的系统、已有模型授权，以及家里是否有 Home Assistant。密钥在音箱或后台主机填写。
3. 已经运行 SP5.5 的音箱可直接部署应用。原厂系统先核对底标、系统和连接情况，再决定是否刷机。固件、驱动和刷机工具按需下载并检查 SHA-256。刷写会覆盖设备数据。

## 选择语音服务

| 档位 | 适合的配置 | 家庭设备控制 |
|---|---|---|
| 标准 | Hermes 网关＋OpenAI Realtime，使用已启用 GPT-Live 的 profile | 由同一 Hermes profile 接入 HA、执行任务 |
| 中配 | 豆包 Seeduplex 语音，启用 Seed Pro 复杂推理时另配方舟 Key 和模型 ID | LX04 可直接发现并接入 HA |
| 低配 | 一个已开通 Seeduplex 的豆包语音 Key，用于日常对话和控灯 | LX04 可直接发现 HA，确认地址后填写 HA 令牌 |

首次部署详见[配置问诊](references/preflight.md)。安装后可按[音箱验收步骤](references/deployment.md)检查唤醒、音频、插话及工具调用。需要重刷系统时见[SP5.5 刷机说明](references/flashing.md)。

## 分发与许可

本仓库公开部署 skill、文档和辅助脚本。Nabu LX04 应用以签名 APK 交付，应用自有源码由开发者私有维护。上游 MIT 代码附有[许可文本](assets/UPSTREAM-MIT.txt)。APK 内的 Emotion Ball 引擎和角色视觉分别适用随附的 LICENSE 和 NOTICE，其中球形角色视觉仅供个人技术学习和研究使用。
