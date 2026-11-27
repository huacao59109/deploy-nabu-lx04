# 安装与验收

## 选择语音模式

本包只有一个 `assets/Nabu-LX04.apk`，版本 0.9-skill（versionCode 9），包名 `dev.herald.lx04`。从技能目录运行 `python scripts/prepare.py verify` 校验签名 APK 文件的固定 SHA-256。已有 SP5.5 直接部署。覆盖升级时 Hermes 沿用原设置；0.3 已配置的豆包双模型自动按中配运行，HA 默认为关闭。0.4 至 0.7 的聊天、Seed Pro 及已启用的 HA 配置均可沿用。

新装首次打开设置页默认显示「标准档」。按问诊推荐点页面顶部的档位，表单会随选择切换。两档豆包勾选 HA 且地址为空时，音箱查找约 4–10 秒。一台自动预填，多台点选匹配的名称和地址，零台可重试或手填；未知地址按[发现零台时如何找回地址](preflight.md)从已登录的 HA 手机应用、浏览器或路由器/NAS 查找。已有地址保留，可按查找按钮重新选择；确认目标后点验证才会使用令牌。

- **标准档**：在 LX04 设置页选「标准档」（Hermes＋OpenAI Realtime），输入自己的 Dashboard 基础地址、用户名、密码和可选 profile。地址保留端口与基础路径，例如 `nas.lan:9119` 或 `https://hermes.example.org/hermes`；省略协议时使用 HTTP，仅用于可信局域网。网关所选 profile 的模式标识为 `gpt-live` 且 `available=true` 才会通过实时语音检查。GPT-Live 是 Hermes 的模式名，具体 OpenAI 模型由网关配置。有 HA 时先核实该 profile 已有工具能否查询目标灯；需要新接入时按[标准档接入 HA](preflight.md)从 Hermes 运行环境发现并验证，然后从音箱验收。
- **中配档**：选中配档，填写 Seeduplex 语音 Key。家中有 HA 时勾选「接入局域网 Home Assistant」，确认发现的地址或手填，再在音箱输入长期访问令牌。需要深度推理才勾选「启用 Seed Pro 复杂推理」，填写方舟 Key 和可用的模型 ID。两项可同时勾选。向下滚动点「验证并启用豆包」，应用只验证语音及已选服务，云端验证可能计费。可随时重开设置修改，改变 HA 地址需重新输入该地址的令牌。已验证的模型 Key 留空可沿用。
- **低配档**：点「低配档」，在「豆包语音 API Key（Seeduplex）」填一个已开通实时语音的 Key，家中有 HA 时勾选「接入局域网 Home Assistant」，确认发现的地址或手填，再在音箱输入长期访问令牌，再点「验证并启用豆包」。只聊天可直接验证语音。低配不调用方舟。从中配切到低配时会移除方舟凭据；继续勾选 HA 且地址相同时可沿用原令牌。两档豆包的凭据都在设备本机加密保存。

从未保存网关地址的 0.1 版升级时，打开设置页填写自己的 Hermes 地址并重新登录。签名不同按下文处理。

## 安装、登录、接管

在 Windows 上先运行 `adb version`。找不到命令时，使用已安装的 Android SDK Platform-Tools，或从 [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools) 获取 Windows 压缩包。解压后把**含 adb.exe 的文件夹**加入本次 PowerShell 会话的 PATH，例如下例（替换成实际目录），再运行 `adb version`。

```powershell
$env:Path = 'C:\Android\platform-tools;' + $env:Path
```

正式连接设备时运行 `adb devices -l`。显示 `unauthorized` 时在音箱上允许这台电脑调试；`offline` 时等系统启动完成并检查连接。空列表时先确认数据线、供电和系统来源；Android 正常开机时的 ADB 与刷机时瞬现的 COM 口不同。已知 SP5.5 但未启用调试，可从原厂桌面的「英语绘本」进入安卓桌面，打开「设置 → 系统 → 关于音箱」，连续点版本号后返回开发者选项，启用 USB 调试并确认授权；桌面入口以实际固件为准。原厂或来源不明的机器无法枚举时，先辨认型号与 ROM，再决定是否进入刷机流程。

从解压后的技能目录打开 PowerShell。以下命令在列表只有一台设备且已授权时自动选中。若连接了多台，保留第一行设置的 APK 路径，根据 `adb devices -l` 核对目标后手动运行 `$serial = '目标 LX04 的完整序列号'`，再继续下面的只读核验。确认后先在原厂桌面测一次「小爱同学」，有多台音箱时也测就近唤醒。

```powershell
$apk = (Resolve-Path -LiteralPath '.\assets\Nabu-LX04.apk').Path
$listing = @(adb devices)
if ($LASTEXITCODE -ne 0) { throw 'ADB 未能列出设备' }
$rows = @($listing | Where-Object { $_.Trim() -and $_ -notmatch '^List of devices attached' })
if ($rows.Count -ne 1 -or $rows[0] -notmatch '^(\S+)\s+device\s*$') {
    throw '请核对 adb devices -l，明确授权状态和目标 LX04 后再继续'
}
$serial = $Matches[1]
```

在写入数据前，只读核对所选设备的型号与系统。

```powershell
adb -s $serial shell getprop ro.product.device
adb -s $serial shell getprop ro.build.fingerprint
adb -s $serial shell sha256sum /system/build.prop
adb -s $serial shell getprop ro.build.version.sdk
adb -s $serial shell getprop ro.product.cpu.abilist
adb -s $serial shell getprop sys.boot_completed
adb -s $serial shell pm path com.xiaomi.micolauncher
```

已核验的 SP5.5 镜像 system.img 中读取到指纹 `XiaoAiTongXue/mi_lx04/mi_lx04:8.1.0/O11019/1626056297:user/test-keys`，其中 /system/build.prop 的 SHA-256 为 `DA6F2CDCC76B134D93FEFDF7BE4BBF80561DE8EB8A42A5D657B475A6B2A5043D`。确认机型 mi_lx04、API 27、支持 armeabi-v7a、boot_completed 为 1。指纹和文件哈希只核对该构建的系统属性，不证明所有分区逐字节相同。对没有刷写记录但这些特征相符的设备，先验证原生仲裁、所需权限及接管能力，能运行即走部署路径。读数不同须先查当前 ROM 的来源，不自动重刷。

**三档必做**：现在执行[刷后默认设置](post-flash.md)，完成独立米家停用和无线 SSH 密钥登录，再返回此处安装 Nabu。

先保存以下命令输出，供原样回退，尤其注意属性原为空、app-op 无记录也是有效值。

```powershell
adb -s $serial shell getprop persist.mi.aivs.ip
adb -s $serial shell cmd appops get com.xiaomi.micolauncher PLAY_AUDIO
adb -s $serial shell cmd appops get com.xiaomi.micolauncher SYSTEM_ALERT_WINDOW
adb -s $serial shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
adb -s $serial install -r -g $apk
adb -s $serial shell pm grant dev.herald.lx04 android.permission.READ_LOGS
adb -s $serial shell dumpsys package dev.herald.lx04 | Select-String 'READ_LOGS|RECORD_AUDIO'
adb -s $serial shell pm path dev.herald.lx04
```

检查每条退出状态、安装 Success、两项权限 granted=true。按 `pm path` 返回的实际路径执行 `adb -s $serial shell sha256sum <实际的base.apk路径>`，与主机 `Get-FileHash $apk` 比较。如果覆盖安装报告签名不匹配，保留原应用数据，优先取得同证书构建；只有明确接受清除登录和数据才卸载重装。打开下列设置页，完成所选档位的验证后再接管；失败时保留原有工作配置。

```powershell
adb -s $serial shell am start -n dev.herald.lx04/dev.hermeskotlin.lx04.SetupActivity --ez settings true
```

以下是沿用 main 的 SP5.5 接管配置。原厂桌面仍是 HOME；保留它及小米底层音频和仲裁服务。Nabu 依赖其原生事件。若已是下列目标值，跳过对应改动；不要在每次启动时反复 force-stop。系统属性需要设备当前管理终端有相应权限，失败时报告并保留可恢复状态。

```powershell
adb -s $serial shell cmd appops set com.xiaomi.micolauncher PLAY_AUDIO ignore
adb -s $serial shell cmd appops set com.xiaomi.micolauncher SYSTEM_ALERT_WINDOW ignore
adb -s $serial shell setprop persist.mi.aivs.ip 127.0.0.1
adb -s $serial shell getprop persist.mi.aivs.ip
adb -s $serial shell am force-stop com.xiaomi.micolauncher
adb -s $serial shell am start -n com.xiaomi.micolauncher/.Launcher
adb -s $serial shell dumpsys activity services dev.herald.lx04
```

再次查询两个 app-op 及 HOME，核对 Nabu 的 SpeakerService 正在前台运行。原机桌面申请悬浮权限时保持关闭，首次配置处理完返回桌面。若用户要撤回接管，按部署前记录分别恢复属性及两项 app-op，无原设置的 app-op 用 default。原属性为空时，PowerShell 用 `adb -s $serial shell "setprop persist.mi.aivs.ip ''"` 并回读。再重启原厂桌面。要停用 Nabu 可 `pm disable-user --user 0 dev.herald.lx04`，需要恢复时 `pm enable dev.herald.lx04`。已接管设备更新不应把当前的 ignore 或回环地址误当成原厂基线。

## 重启后确认桌面和语音接管

先在设置页完成所选服务的验证并启用语音。首次授权、登录或验证尚未完成时，不能验收开机接管。与 SSH 和米家的复核共用一次正常重启。等系统与 Wi-Fi 就绪，观察开机直到原厂待机桌面稳定；MicoLauncher 的“显示在其他应用的上层”页可能短暂出现。若出现，应自行退出，开关保持关闭。当前 APK 仅在真正开机、语音已启用时，轮询约 30 秒识别这一特定权限页；没有弹出也正常。录音、USB 授权或用户主动打开的设置页按其用途正常处理。

```powershell
adb -s $serial shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
adb -s $serial shell cmd appops get com.xiaomi.micolauncher PLAY_AUDIO
adb -s $serial shell cmd appops get com.xiaomi.micolauncher SYSTEM_ALERT_WINDOW
adb -s $serial shell getprop persist.mi.aivs.ip
adb -s $serial shell dumpsys activity services dev.herald.lx04 | Select-String 'SpeakerService|isForeground'
adb -s $serial shell dumpsys activity activities | Select-String 'mResumedActivity'
adb -s $serial logcat -d -s 'NabuLX04:I' '*:S' | Select-String '开机已返回原厂待机桌面'
```

核对 HOME 为原厂 MicoLauncher、两项 app-op 均为 ignore、云端语音地址为 127.0.0.1，SpeakerService 已启动。用新启动周期的顶层界面和实际屏幕判断；日志标记只在自动退出权限页时产生。若页面持续停留，先核对目标包、当前启动周期、READ_LOGS 授权和语音是否已启用。修正后正常重启复验。不要为消除这一页授予悬浮权限或屏蔽系统设置。旧测试机若把 Nabu 设为 HOME 或曾停用原桌面，先核实已有改动，再恢复已确认的原厂桌面和原生唤醒基线。

## 真机验收和定位

| 操作 | 看什么 |
|---|---|
| 靠近本机说「小爱同学」，再说「只说蓝色雨伞」 | 原生选中本机后才开 Nabu；大表情球、实际播报、第一行绿色用户字幕、第二行白色 AI 字幕。若有另一台，在另一台旁重复，本机应保持待机。 |
| 让它慢慢数数，中途纠正，接着追问 | 正常插话能让出话轮、追问不用重唤醒。家人旁聊单独测试有没有误停、误答或误派；绿色字幕显示旁聊本身符合设计。 |
| LX04 获选后提一个容易触发原厂卡片的问题 | 一句唤醒应答可保留；随后只有 Nabu 回答并显示内容。无原厂公式卡片、重复朗读或“这个问题我还在学习”字幕。在支持图片的标准档让 Hermes 显示图片，再说“把图片关掉”，确认恢复大球并能直接追问。 |
| 在日常音量播报时安静片刻，再开口插话 | 静听时无自问自答，人声能打断且第一句话听清。标准档使用 WebRTC 软件回声消除；豆包使用通话录音源，并在平台支持时启用系统 AEC，以实听判断。 |
| 挂断后再做两轮原生唤醒；有第二台时交替靠近 | 不点屏、不重开应用。LX04 两次获选均能听清新一句，挂断后回原厂待机；靠近另一台只有另一台回答。借此验证 Nabu 已释放录放音与音频焦点，原生麦克风能接回。 |
| 标准档：提出用户环境中可核对的只读 Hermes 任务 | 看 Hermes 图标、任务实际到达与结果。动态记录可从 logcat 的 LiveCallLifecycle、NabuLX04 查 model_handoff、match_accepted、submit_Sent 及任务结束。只说“查一下”不足以验收。 |
| 中配已启用 Seed Pro：先闲聊，再用明确数据提一道多步比较题，追问进度 | 闲聊预期零次推理；复杂题查 `NabuLX04` 的 `Seed Pro dispatch` 一次及 `Seed Pro result`，听取同一语音会话的真实结论。记录是否误派、漏派或重复。未配置 HA 时，要求控制设备应说明能力范围。 |
| 中配已启用 Seed Pro：在推理过程中挂断，重新唤醒后另问一题 | 原通话的迟到结论不会在待机或新会话中播报。验证远场、插话和旁聊时分别记录听感，离线回放不能证明真机回声消除或模型选路效果。 |
| 豆包低配或中配已接入 HA：先查用户授权且当前亮着的测试灯，以该灯在 HA 中的实际名称说“关掉〈灯名〉”，再问“关了吗” | 核对 HA 执行回执、测试灯由亮变灭，以及复查读到关闭状态。仅勾选 HA 时也应能完成上述步骤，日志只有 HA 派发与回执，没有 Seed Pro 派发。复核相同调用仅执行一次；超时或部分失败要如实播报。无法识别目标时核对中文别名与 Assist 实体开放设置。 |
| 标准档已接入 HA：从音箱查询测试灯状态，控制一次后追问状态 | 在所选 Hermes profile 核对 HA 工具的调用、回执和灯的实际状态。追问应只产生状态查询。 |
| 低配未启用 HA：只填语音 Key，唤醒后聊天、插话，再给一条设备控制命令 | 聊天和继续接话正常；不应注册 HA / Seed Pro 工具，也不应宣称执行了控制。 |
| 通话中按实体音量键，说「挂断」，再重新唤醒 | 音量按实际听感变化，挂断回到原厂待机，能再由原生唤醒。完成后在可重启时验证断电启动或正常重启后服务自启。 |

- 无唤醒：先检查 READ_LOGS、SpeakerService、Wi-Fi、原厂 HOME 和仲裁。原厂 `from(0)=VPM` 只是听到唤醒；本机获选还有 `from(1)=MDSPPECH ... WAKEUP_NORMAL` 及 TtsCard 有声唤醒事件，另一台获选可见 WAKEUP_CANCEL。不要为了使其开通就绕过仲裁。
- 已唤醒但无回答：标准档查登录/profile、网关和 WebRTC；豆包两档查 Seeduplex 授权、网络和音频输出。仅启用 Seed Pro 时需要排查方舟推理权限；豆包控灯失败查音箱到 HA 的连接、令牌及 Assist 可见实体；标准档查 Hermes profile、工具权限和 Hermes 到 HA 的连接。系统提示音也无声时，先看 `dumpsys audio` 的设备和静音状态；可用独立媒体播放做对照。请勿因无声就重刷。
- 有回答无派发：把 model_handoff、匹配/过滤、submit_Sent、任务结束分开定位，保留事件时间和 ID，日志中避免打印家庭对话正文、凭据或密钥。
