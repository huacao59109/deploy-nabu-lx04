# SP5.5 首启后的两项必做工作

刚刷好的音箱和已刷 SP5.5 的三档部署都走这里。在[安装与验收](deployment.md)中选定已授权的 USB 序列号 `$serial`、核实 ROM、完成 Wi-Fi 初始化和原生唤醒基线后执行。重复部署时先复用并验证现有设置。两项分别记录结果；其中一项受阻，继续能执行的另一项，报告具体缺项。

## 停止米家并禁止自启

从技能根目录运行。脚本仅操作用户 0 的独立米家应用 `com.xiaomi.smarthome`，会检查停用状态及其主、子进程。包本来就不存在时记录“未安装”。保留米家数据、原厂桌面 `com.xiaomi.micolauncher`、音频及就近唤醒服务。

```powershell
adb -s $serial shell dumpsys package com.xiaomi.smarthome | Select-String 'User 0:'
python scripts/post_flash.py disable-mijia --serial $serial
if ($LASTEXITCODE -ne 0) { throw '米家停用或验证失败，请保留实际输出' }
```

保存第一行的初始状态。以后用户要求恢复时，原来 `enabled=0` 用 `adb -s $serial shell pm default-state --user 0 com.xiaomi.smarthome`，原来显式启用（`enabled=1`）用 `pm enable --user 0 com.xiaomi.smarthome`。原为“使用前停用”（enabled=4）则用 `pm disable-until-used --user 0 com.xiaomi.smarthome` 恢复；原已持久停用或未安装的保持原样。上述 pm 命令均在同一目标的 ADB shell 中执行。若系统报告权限不足，检查当前授权的管理终端；不要通过删除系统 APK 处理。

## 配置无线 SSH

用用户自己的管理电脑和可信局域网。按实际状态选择入口。

- **已有可用的 SSH**：沿用管理电脑已信任的主机记录、端口和密钥。例如已有 OpenSSH 别名时，运行下面两行，**重启后重复同一条 ssh 命令**。没有别名时，在原先成功的登录命令上加入 `-o BatchMode=yes -o StrictHostKeyChecking=yes` 和末尾的只读命令。核实是目标局域网音箱，输出为 `mi_lx04` 和实际账号的 `uid=…`。成功即可转到“重启验收”，跳过新装示例。重启后失败则检查原服务自启设置。

```powershell
$knownSpeaker = Read-Host '这台 LX04 原有的 SSH 主机别名'
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes $knownSpeaker 'getprop ro.product.device && id'
```

- **尚无可用的 SSH**：先运行 `adb -s $serial shell pm list packages --user 0 org.galexander.sshd`。未装 SimpleSSHD 才执行以下下载和安装。已有此包、但从未登记密钥时，跳过下载和安装，从步骤 1 开始配置，使用实际端口和路径。若已有他人配置的授权密钥，先用所有者原有登录方式追加管理公钥，保留已有授权。签名或配置来源不明时先查明。

```powershell
$sshApk = python scripts/post_flash.py fetch-ssh
if ($LASTEXITCODE -ne 0) { throw 'SimpleSSHD 下载或 SHA-256 校验失败' }
adb -s $serial install $sshApk
if ($LASTEXITCODE -ne 0) { throw 'SimpleSSHD 安装失败' }
```

脚本按需下载并校验 F-Droid 的 SimpleSSHD 27。离线时可把同名原包 `org.galexander.sshd_27.apk` 放进 `%LOCALAPPDATA%\Nabu-LX04\downloads` 后执行同一命令。缓存校验失败会停止。

1. 运行 `adb -s $serial shell am start -n org.galexander.sshd/.SimpleSSHD`。在应用 Settings 打开 **Start on Boot** 和 **Foreground Service**。新装使用默认端口 2222，SSH Path 和 Home Directory 使用应用私有目录。首次点 **Start**。已有服务改设置后按上游说明重启服务。Agent 可操作界面时直接代办。[SimpleSSHD 官方说明](https://www.galexander.org/software/simplesshd/)
2. 检查 Windows 上有 `ssh` 和 `ssh-keygen`。选这台音箱的专用密钥，路径存入 `$key`。首次可用下例创建；重跑时保留现有文件。私钥和口令只留在管理电脑，使用口令的密钥应先在本机 SSH agent 解锁再做无人值守验收。

```powershell
$key = Join-Path $env:USERPROFILE ".ssh\lx04-$serial"
New-Item -ItemType Directory -Force (Split-Path $key) | Out-Null
if (!(Test-Path $key) -and !(Test-Path "$key.pub")) { ssh-keygen -t ed25519 -f $key }
if (!(Test-Path $key) -or !(Test-Path "$key.pub")) { throw '请核对管理电脑的密钥对' }
```

3. 新装时通过当前已核实的 USB 目标建立临时转发，首次主机指纹从这条连接登记。Windows 首次提示时在本机确认；SimpleSSHD 若显示一次性口令，由用户在本机 SSH 终端输入。只追加公钥。下面命令适用于 SSH Path 与 Home Directory 相同的新装默认设置。已有 SimpleSSHD 若采用其他端口，把下例 2222 换为其实际端口；SSH Path 与 Home Directory 不同时，用应用显示的 SSH Path 定位 authorized_keys。已有授权但缺原管理密钥时，报告需要所有者协助。

```powershell
$port = 2222
$aliasName = "nabu-lx04-$serial"
$bindPort = adb -s $serial forward tcp:0 "tcp:$port"
if ($LASTEXITCODE -ne 0 -or $bindPort -notmatch '^\d+$') { throw 'USB 转发失败' }
$opts = @('-o', "HostKeyAlias=$aliasName", '-o', 'IdentitiesOnly=yes', '-i', $key)
try {
    $line = (Get-Content -Raw "$key.pub").Trim()
    if ($line -notmatch '^(ssh-ed25519 [A-Za-z0-9+/]+={0,2})(?:\s|$)') { throw '请核对 Ed25519 公钥' }
    $pub = $Matches[1]
    ssh @opts -o StrictHostKeyChecking=ask -p $bindPort 127.0.0.1 "umask 077 && (grep -Fxq '$pub' authorized_keys 2>/dev/null || echo '$pub' >> authorized_keys) && chmod 600 authorized_keys"
    if ($LASTEXITCODE -ne 0) { throw '公钥登记失败' }
} finally {
    adb -s $serial forward --remove "tcp:$bindPort"
}
```

4. 从音箱 Wi-Fi 设置或 `adb -s $serial shell ip -4 addr show wlan0` 取得本机局域网 IP，填写 `$speakerIp`。在用户电脑运行下例，须返回 `mi_lx04` 与实际账号的 `uid=…`。新装使用上一步的参数，已有 SSH 用原先信任的主机记录、密钥和端口。默认会话是 SimpleSSHD 的应用账号。系统级软件管理继续使用已授权的 ADB。保持局域网访问，无需在路由器映射端口。

```powershell
$speakerIp = Read-Host 'LX04 的局域网 IP'
ssh @opts -o BatchMode=yes -o StrictHostKeyChecking=yes -p $port $speakerIp 'getprop ro.product.device && id'
if ($LASTEXITCODE -ne 0) { throw '局域网密钥登录失败' }
```

## 重启验收

与 Nabu 的首次重启验收合并做一次。等系统正常启动、Wi-Fi 恢复后，在管理电脑上再次通过**局域网地址**执行上述 SSH 登录，期间不要手动启动 SimpleSSHD。若 DHCP 换址，核对新地址并验证原主机指纹。用同一已授权 ADB 目标执行 `python scripts/post_flash.py check-mijia --serial $serial`，确认包已停用且无进程，或原本未安装。最后实测「小爱同学」与就近唤醒。仅能验包、未重启或缺少实际设备时，将相应项记为待验。

如用户要求撤销本次新增的 SSH，可在 SimpleSSHD 关闭 Start on Boot 并点 Stop；保留用户原有服务和密钥。
