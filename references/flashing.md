# LX04 SP5.5 刷写（Windows）

适用范围为底标 LX04、MT8167、eMMC。供电采用原装或固定 5 V / 2 A 适配器；刷机的数据口或独立供电数据 Hub 须稳定输出 5 V。避免手机快充头、诱骗升压线和 9 V / 12 V 输入，过压可能损坏主板。参考机起点是原厂 2.42.118。使用社区 SP5.5；这是本次实机成功用过的固定材料。哈希用于核对副本一致性。型号不同、项目或存储不符时停止。系统已可部署时直接转安装。

## 准备及只读握手

- 使用已传过文件的 Micro‑USB 线和稳定的数据口。LX04 以 USB 供电，正常供电规格为 5 V / 2 A；电脑供电不足时可用有独立供电、能传数据的 Hub。保留已知正常的端口，写入期间保持供电。
- 仅在刷机路径运行 stage。它从社区资源目录按需下载固件和刷写工具到本机缓存，逐件通过固定 SHA-256 校验后才解包并生成配置。以 PowerShell 在技能目录运行下例，目标换成新的、当前账号可写且无空格的 ASCII 绝对路径，预留数 GB 空间。Python 3 可用。
```powershell
python scripts/prepare.py stage D:\LX04-stage
```
- 记录开始时间。用 Windows 设备管理器或 `Get-PnpDevice -Class Ports`、`C:\Windows\INF\setupapi.dev.log` 观察音箱端断电再接入的瞬间。识别 MediaTek PreLoader USB VCOM，实机记录 USB VID_0E8D、PID_2000。COM 号由这台电脑动态分配；旧的灰色记录不足以确定目标。首次辨认时可只按音量＋重新上电，约 3 秒松开。参考机在独立供电 Hub 上正常重新上电也能枚举。正常 Android 下的 MTP/ADB 与这个短暂启动端口是不同接口。
- Windows 已正确绑定驱动时跳过安装。若预加载接口有驱动错误，在设备管理器核对硬件 ID，另行执行 `python scripts/prepare.py fetch driver`，解压输出路径中的已校验驱动包，用对应系统架构的签名 VCOM INF 安装；Windows 提权由用户完成。端口不出现时先用同口同线接其他数据设备作对照，USB 未枚举时安装 ADB 驱动无助于此阶段。
- 工具目录包含 `_SPFT.exe`；配置使用同包 `DA_Mi_Hikaru-resign.bin`、`auth_sv5.auth` 和 `sp5.5/Scatter_Mi_Hikaru-resign.txt`。使用固件配套的正常签名认证流程。校验或认证失败时核对材料和型号，停止写入。
- 建议先运行生成的 `read-gpt.xml`（只读 32 KiB）。先拔下音箱端，保留 Hub 通电。把下面的 COM7 换成刚刚观测到的端口。命令在工作目录启动一个后台进程，然后另读最新 QT 日志。看到本轮 `Searching user specified com port` 并核对端口后，再请用户接回同一口。
```powershell
$stage = 'D:\LX04-stage'
$port = 'COM7' # 替换为目标实测值
$tool = Join-Path $stage 'tool/FlashTool'
$job = Start-Process -FilePath "$tool/_SPFT.exe" -WorkingDirectory $tool -ArgumentList @('-p',$port,'-i',"$stage/read-gpt.xml") -PassThru -WindowStyle Hidden
```
  工具日志默认在 `%ProgramData%\SP_FT_Logs\SP_FT_Dump_*\QT_FLASH_TOOL.log`，按进程启动时间识别本轮；以工具目录的 option.ini 为准。检查只读成功及 `gpt-head.bin` 的签名、GPT 头和分区表 CRC，必要时用新文件名复读比对。若表超出首 32 KiB，按头部给出的尺寸补读。确认原机分区与目标 scatter 相容。参考机 userdata 预设容量比原机少 344 MiB，因而使用 Firmware Upgrade 处理布局，不把这个差值当作其他机器的常量。
- 提供保留本机备份的选择。可用工具 Readback 读取本机 EMMC_BOOT_1、BOOT_2、USER；容量从该机存储信息取得，将各区起始地址、长度、读回结果、复读校验和 SHA-256 保存在本机私有目录。单次握手或 GPT 成功不等于长传输可靠。参考机多次读回超时，只得到部分备份，没有验证完整恢复。明确要求备份的用户，未完成就停在写入前；明确接受跳过的，在记录中注明。不要把一台音箱的备份分发给另一台。

## 写入与首启

只读校验命令为 `python scripts/prepare.py check-gpt D:\LX04-stage\gpt-head.bin`。它校验原机主 GPT 和分区项的 CRC，并列出各区起点和字节数，供与 scatter 对照；不读取 USB，也不写设备。

1. 确认只读进程已退出；记录目标、连接端口、固件哈希、备份状态及覆盖 userdata、启动区的影响。得到针对该机的写入授权再继续。若设备持续断连，应先排除供电和接触问题。
2. 音箱端断电，沿用上面的 Start-Process 命令，**仅把最后的配置文件改为 `$stage/firmware-upgrade.xml`**。这是实际成功使用的 `firmware-upgrade / FIRMWARE_UPGRADE` 配置。保留 scatter 自带下载列表。不要选 Format All + Download，不要手工格式化或修改分区、切换通用 DA。
3. 等待本轮日志显示工具已经在等正确的 COM，再让用户正常接回同一数据口。写入期间不要拔线、重启或启动第二个工具。以本轮日志的 `DADownloadAll ... Download Succeeded` 和最终成功状态作为写入完成依据；握手成功、Format Succeeded 或进程退出均不能单独证明成功。写入中断时先保存日志和最后阶段，保持供电，判断端口和启动状态。不存在已验证的通用救砖流程，不自动循环重写。
4. 成功后观察首启。若已经出现开机画面，保持供电；仅在工具已结束且一直黑屏时正常断电接回一次。完成 Wi-Fi/原厂初始化。SP5.5 可先直接试 `adb devices -l`；如未开放，社区实机路径为小爱桌面「英语绘本」进入安卓桌面 → 设置 → 系统 → 关于音箱，连续点版本号，返回开发者选项打开 USB 调试并允许当前电脑。不同桌面版本以实机为准。通过 `sys.boot_completed=1`、新系统指纹、API/ABI 和桌面确认首启；转[安装与设备核验](deployment.md)，接着完成[默认 SSH 和米家设置](post-flash.md)，再安装 Nabu。

材料来源可追溯到[社区 LX04 固件目录](https://xiaoai.qgmzmy.me/lx04/rom)和[SP5.5 上手记录](https://blog.xuxiny.top/index.php/2025/06/22/1176/)。默认缓存目录为 Windows 的 %LOCALAPPDATA%\Nabu-LX04\downloads。可用 --cache 指定装有同名文件的目录，来自下载、缓存或手工拷贝的文件都执行相同的 SHA-256 校验。已确认缺驱动且尚未 stage 时，可在 stage 命令末尾加 --with-driver 一并准备。资源不可达时可从该目录手工取得原包或使用自己的已验证缓存；遇到摘要不符应停止，勿以新摘要覆盖固定值。
