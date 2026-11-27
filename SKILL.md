---
name: deploy-nabu-lx04
description: 在 Windows 上为小米小爱触屏音箱 LX04 选择并部署 Nabu 语音助手。先了解硬件、局域网智能体、实时模型和网络条件，按需刷写 SP5.5，用同一 APK 配置 Hermes＋OpenAI Realtime（GPT-Live）或豆包实时语音（单 Key、可扩展 Seed Pro）。家中有 Home Assistant 时按所选档位协助接入。
---

# 部署 Nabu LX04

收到 ZIP 后先在 Windows 上完整解压。在 Codex 打开解压后的 `deploy-nabu-lx04` 文件夹（里面应直接看到 `SKILL.md`、`scripts` 和 `assets`），可以说「按这里的 SKILL.md 帮我配置刚拿到的 LX04」。以下相对路径均从这个文件夹运行。部署者先用 `python --version` 检查本机 Python 3；只有 `py` 启动器时用 `py -3` 替代命令中的 `python`。缺少时可从 [Python for Windows](https://www.python.org/downloads/windows/) 安装 Python 3 并验证。离线且本地缺必要材料时说明缺项。

1. 首轮问诊先说明：LX04 上的米家将停用；保留原生唤醒与就近仲裁，原有问答和指令改由 Nabu 接管。提醒使用原装或固定 5 V / 2 A 适配器，避免手机快充头、诱骗升压线和高于 5 V 的输入。再读[配置问诊和选档](references/preflight.md)。所有档位都先了解用户有无 Home Assistant（HA）。有 HA 就将接入和验收列入部署方案，先确认授权实体和测试目标。地址未知时从实际使用 HA 的主机发现：豆包在 LX04 设置页查找，标准档复用所选 Hermes profile 的可用 HA 工具；需要新发现时，按问诊文档从真实 Hermes 主机或容器取得位置标识，再从同一环境发现和验证；用户明确跳过时尊重选择。语音和推理凭据决定档位。复用本次用户已经提供的事实，把影响选择的缺项一次问清。离线走查可验包、模拟用户配置或用已校验的本地缓存准备刷机目录；跳过真实 mDNS、设备连接、刷写和在线凭据验证。
2. 向用户给出一个推荐方案，说明选档依据、还缺的条件、涉及的主机、是否刷机、费用和验收方式。部署请求范围内能做的配置和验证由你执行。需要新购服务、写固件或改变家庭网络时，按用户给出的授权范围实施。
3. 三档共用签名 APK。先在技能目录运行 `python scripts/prepare.py verify`。已有可用 SP5.5 直接转[安装与验收](references/deployment.md)，全程跳过刷机材料。原厂系统且用户已选好可用方案、确认写盘后，按[刷机流程](references/flashing.md)按需获取并校验固件、工具和驱动。找不到 ADB 时先核实系统与线缆。
4. 首启或已有 SP5.5 核验通过后，三档均先完成[刷后默认设置](references/post-flash.md)：配置局域网 SSH 密钥登录与开机自启，停止独立米家并禁止自启。完成语音配置后重启，逐项复核 SSH、米家和原厂权限页自动退出，再报告部署结果。
5. 保留原厂桌面、原生就近唤醒和用户的现有网络。按所选档验证双向音频、插话、连续对话、挂断和再次唤醒；标准档额外查 Hermes 任务实收，中配启用 Seed Pro 时查复杂推理派发。凡接入 HA，都查真实状态、一次控制和随后的状态复查。低配只需一个模型 Key。区分离线验证、云端授权和真机听感。
