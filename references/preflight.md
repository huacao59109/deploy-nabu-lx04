# 安装前如何选档

在选档、下载或刷机前先告知实际影响：音箱上的米家将无法使用，小爱原有问答、屏幕卡片和指令由 Nabu 接管，保留原生唤醒和多机仲裁。若用户依赖原厂功能，先讨论是否适合部署。日常供电使用原装或固定 5 V / 2 A 适配器，避免使用手机快充头、诱骗升压线或高于 5 V 的输入。提醒也适用于已刷 SP5.5 的音箱。[小米官方规格](https://www.mi.com/aispeaker-touch/specs)

先向用户收集影响部署的信息。已知道的内容直接带入方案，不要求重复填写。用户只需说“有、没有或不确定”，真实凭据在网关或音箱本机输入。

先按来访者已说的目标分流，再从下文选问相关条件。说“只有一个豆包语音 Key，只想聊天”时，确认该 Key 已开通 Seeduplex 实时语音就推荐低配，继续核实设备、系统、网络和有无 HA。说“有 HA，想关灯”时，确认 Key 已开通 Seeduplex 后即可推荐低配，未知 HA 地址不影响选档。新装默认显示标准档：点「低配档」→ 填语音 Key → 勾选「接入局域网 Home Assistant」，把地址留空，等音箱查找。一台自动预填，多台选自己的，找到后再为该实例准备 HA 长期访问令牌；仅在用户还希望使用 Seed Pro 做复杂推理时，再询问方舟 Key 和可用模型 ID。

- **设备和目标**：确认底部型号、当前系统（原厂、SP5.5 或未知）、是否能用 Windows 和 ADB、有无第二台小爱需要就近唤醒。希望控制设备、委派家庭任务，还是日常对话加复杂问题推理即可？
- 三档部署方案均说明两项刷后设置：为管理电脑配置局域网 SSH，停用音箱上的独立米家。已有 SP5.5 同样核验。保留原生就近唤醒；夜间时段、蓝牙输出、视频应用精简等沿用用户选择。
- **现有后台**：是否已有可用的 Hermes Dashboard，或其他局域网智能体？有则询问服务名、基础地址（含端口和路径）、认证方式、可用 profile。需要新建服务时再问可常开的 NAS/电脑、系统、部署方式及管理权限。
- **Home Assistant**：家里是否已有 HA？有就协助接入当前档位，问清目标灯或其他实体和已有授权；已知地址可以直接使用。标准档由 Hermes 主机访问 HA，优先复用所选 profile 已有工具；两档豆包由音箱访问 HA，核对内置中文 Assist 是否识别目标。让用户在相应主机或音箱填写令牌。若用户明确跳过，或发现与手填都无法取得地址、缺授权或网络，说明当前状态和补齐步骤。
- **模型和网络**：已有的 Hermes profile 是否已启用 GPT-Live？是否有可计费的 OpenAI Realtime API 权限？豆包用户是否有 Seeduplex 语音授权？启用 Seed Pro 时再核对方舟权限与模型/接入点 ID。只检查所选服务的网络路径，包括控灯时 Hermes 主机或音箱到 HA 的连接。有无可使用的现成网络出口？不知道的项目可在授权范围内代查。
- **补齐条件**：如有缺项，确认用户是否接受相关云服务费用、在指定主机安装 Hermes、使用其已有合规网络出口，或者选择另一个能满足用途的档位。用一段话列出推荐、缺项、实施位置和成功标准，避免无条件先刷机。

| 实际条件 | 怎样帮用户实施 |
|---|---|
| 已有 Hermes 与 OpenAI 实时语音 | 优先标准档。通过 Dashboard 密码认证、指定 profile 的 GPT-Live 状态，再用真实通话验证媒体双向可达。已有可用 profile 时用户无需另交模型 Key。有 HA 时按下文「标准档接入 HA」配置并验收。 |
| 有 OpenAI API，缺 Hermes，希望控制设备 | 在用户指定的常开主机上按其系统安装 Hermes Agent、启用有密码认证的局域网 Dashboard、配置 profile 的实时语音以及所需任务工具。部署完验证端到端调用。按当前版本选择安装方式，见 [Hermes Dashboard](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)。 |
| 有其他局域网智能体 | 查清是否兼容 Dashboard 的密码登录、网关 WebSocket、会话任务和 voice-live SDP 接口。普通聊天 API 地址无法直接填入。若不兼容且要执行任务，可以部署 Hermes 并接入对方已有工具，在一个只读任务上验收；若只需语音和推理，按语音与推理需求在中配和低配中选择。 |
| 有 Hermes 但没有 OpenAI 实时额度，或缺网络出口 | 帮用户检查 profile、账号模型权限、额度及出错位置。先测试现有出口，再按授权配置具体主机/音箱所需的网络服务；HTTP 代理可连通登录接口，并不保证 WebRTC 音频通路。如能访问火山服务，按现有凭据和所需能力选择中配或低配。 |
| 有 Seeduplex 语音 Key 和 HA，希望声控设备 | 一个语音 Key 即选低配；需要 Seed Pro 时选中配。两档均勾选「接入局域网 Home Assistant」。协助启用中文 Assist、设置目标实体的名称、别名与区域，并只向内置 Assist 开放希望控制的实体。在“个人资料 → 安全”创建当前用户的长期访问令牌，优先使用专用非管理员账户。在音箱勾选接入 HA 后先发现地址，再确认实例、填写令牌。先在 HA 的 Assist 界面用中文试查设备状态，再在用户同意的测试设备上验收控制。HTTP 仅用在可信局域网，亦可使用音箱信任的 HTTPS。 |
| 有 Seeduplex 语音 Key，需要 Seed Pro 做复杂推理 | 选中配，勾选「启用 Seed Pro 复杂推理」，另填方舟 Key 和模型 ID。家中有 HA 时同时接入 Home Assistant。 |
| 有 Seeduplex 语音 Key，只想聊天 | 选低配，直接验证语音。无需 NAS、Hermes、方舟或 HA。 |
| 只有方舟 Key、豆包消费端账号或尚无任何模型权限 | 若只想聊天，协助用户开通可计费的 Seeduplex 语音 API；想要多步推理则再检查方舟 Seed Pro 模型权限。补齐已选档位的条件再继续安装。 |

**标准档接入 HA。** 先确认音箱使用哪个 Hermes profile、它在哪台主机或哪个容器运行。若这个 profile 已能实查目标灯，复用已有配置即可。需要发现或验证新地址时，部署者在已确认的 Hermes 运行环境使用随包的 [find_ha.py](../scripts/find_ha.py)。如果目前只能登录 Dashboard，没有对应主机或容器终端，先解决目标访问；不要退到 Windows 部署电脑扫描。

例如，Windows 部署电脑已有一个指向 NAS 的 Docker context 时，在解压的 skill 目录运行下面的 PowerShell。示例中的 context 和容器名由部署者按实际部署替换。先核对 Docker endpoint 与容器确实对应目标 Hermes，然后始终经同一 context 和容器执行：

```powershell
$ctx = 'nas-hermes'
$container = 'hermes'
docker context inspect $ctx --format '{{.Endpoints.docker.Host}}'
docker --context $ctx ps --format '{{.Names}}'
docker --context $ctx cp ./scripts/find_ha.py "${container}:/tmp/nabu_find_ha.py"
if ($LASTEXITCODE -ne 0) { throw '无法复制到目标 Hermes 容器' }
$runtime = docker --context $ctx exec $container python3 /tmp/nabu_find_ha.py --runtime-id
if ($LASTEXITCODE -ne 0 -or $runtime -notmatch '^[0-9a-f]{24}$') { throw '未取得目标 Hermes 运行位置' }
docker --context $ctx exec $container python3 /tmp/nabu_find_ha.py --expect-runtime $runtime --discover-only
```

一台时向用户展示地址，多台让用户按名称和地址选择。用户确认目标后，沿用上面的 PowerShell 会话与容器验证：

```powershell
$haUrl = Read-Host "已确认的 HA 基础地址"
docker --context $ctx exec -it $container python3 /tmp/nabu_find_ha.py --expect-runtime $runtime --url $haUrl
```

没有远程 Docker context 时，可通过既有 SSH 或 NAS 管理界面把脚本放进实际容器并打开容器终端；裸机安装则进入 Hermes 主机终端。在目标终端用 `python3 find_ha.py --runtime-id` 读取标识，再用 `python3 find_ha.py --expect-runtime <标识>` 交互查找并验证。始终从已经确认的目标取得标识，不在部署电脑上生成标识代用。Linux 主机或容器重建后应从目标重新取得标识。

发现需要该 Python 环境有 `zeroconf`。缺少时可在目标运行环境的虚拟环境安装，或手填地址跳过发现。验证仅用标准库，向已确认地址发只读的 `GET /api/config`。当 profile 已加载且 `HASS_URL` 与所选地址相符时可沿用 `HASS_TOKEN`，否则在目标主机的交互终端隐藏输入。脚本验证成功后再配置插件。跨 VLAN 或容器桥接阻隔组播时，仍在相同 Hermes 运行环境验证手填地址。

需要新接入时，在 Hermes 主机核对版本；具备官方插件目录且兼容当前插件（Hermes ≥ 0.21.5）的版本，在该 profile 运行 `hermes -p <profile> plugins install homeassistant`，默认 profile 用 `hermes plugins install homeassistant`。把 HA 基础地址和长期令牌配置在该 profile 的 `HASS_URL`、`HASS_TOKEN`，让对应 Hermes 服务重新加载配置，保留其他 profile。旧版自带 HA 工具时直接配置该工具。用目标实体核验 `ha_get_state`，从 LX04 发一次控制后复查状态。按用户所选实体设置插件访问范围，例如支持时设置 `HASS_ENTITY_ALLOWLIST`。[Hermes 官方 HA 指南](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/homeassistant)

**低配和中配准备 HA 控灯。** 若尚不清楚 HA 地址，可在确认系统可部署后先装 APK，进入音箱设置页发现实例。仅查找地址无需令牌；确认是自己的 HA 后，再用已登录的 HA 账户准备令牌和测试灯。在 HA 网页进入「设置 → 语音助手」，选用中文且使用内置 Home Assistant 对话代理的助手。在同页的「公开／Expose」中，核对测试灯已向 Assist 开放，并记下名称、别名和区域。在 Assist 对话框选择该助手，用键盘输入「〈灯名〉现在开着吗」；读到正确状态后再配置音箱。若控台菜单随版本或语言变化，可从灯的实体设置找到语音公开选项。音箱使用内置中文代理，即使其他自定义助手能识别这盏灯，也要在内置助手中核对。

**发现零台且不知道地址。** 先在已经能访问 HA 的手机上打开伴侣应用设置，查看该服务器的内部连接地址；也可从正在家中使用的浏览器地址栏取得。两者都没有时，查看路由器的 DHCP 客户端列表或 NAS 上 HA 容器的端口映射，核对哪台设备运行 HA。常见端口为 8123，反向代理和容器可能使用其他端口。豆包回音箱，标准档回 Hermes 终端，用确认过的协议、地址和端口验证；仍找不到时，先使用已选档位的语音功能（含标准档 Hermes＋OpenAI），稍后在原档位补接 HA。

在豆包设置页勾选 HA 后，空地址会触发短时查找：发现一台自动预填，多台列出名称和地址供选择。保留已有地址；可点「重新查找 HA」或手填。确认显示的目标实例后再输入令牌并点验证。手填时使用用户平时用于打开 HA 网页的**局域网基础地址**，例如 `http://192.168.1.20:8123`（示例，换成实际地址）。保留反向代理前缀，去掉仪表盘路径和 `/api`；`localhost` 在音箱上指向音箱自身。令牌填在独立的「HA 长期访问令牌」框，直接填令牌本身。HA 地址应由音箱直接访问，保留部署前缀及端口，无需公网映射。接入验证只检查授权和 Conversation 组件；实际可控范围由实体开放设置和中文意图支持决定。超时后先查状态。暂时无法提供 HA 时，可先用低配聊天；已有方舟授权且需要复杂推理时也可先启用 Seed Pro，稍后再添加 HA。[实体开放设置](https://www.home-assistant.io/voice_control/voice_remote_expose_devices/) · [HA Conversation 接口](https://developers.home-assistant.io/docs/intent_conversation_api/)

**服务端核验。** 标准档需要 Dashboard 支持 `auth/password-login`、`api/auth/ws-ticket`、`api/ws`、profile 下的 `api/audio/voice-live/status`（`mode=gpt-live` 且 `available=true`）和 `api/audio/voice-live/session` 返回 WebRTC 应答。豆包两档均创建一次无麦克风语音会话，可能计费。仅勾选 HA 时，额外验证局域网 HA 授权及 Assist。仅在启用 Seed Pro 时才向方舟发一条可能计费的验证请求。单独报告失败的阶段，不把登录成功视为音频实测成功。[Seeduplex 语音接口](https://docs.volcengine.com/docs/doubao-voice/end-to-end-real-time-voice-full-duplex-version?lang=zh) · [方舟模型列表](https://docs.volcengine.com/docs/ark/model-list?lang=zh)
