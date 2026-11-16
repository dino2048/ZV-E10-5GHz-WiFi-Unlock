# AI Agent 辅助安装

**简体中文** | [English](install.md)

本指南由用户与 AI Agent 配合执行，使用配套 toolkit 完成连接、备份和修改。Windows 的操作入口面向 ZV-E10 第一代 2.03；平台范围见[验证说明](evidence.zh-CN.md)。

2.03 的所有服务端命令都要带 `--backend jiritsu --firmware 2.03 --owner-authorized-exec`。Jiritsu 会临时上传加载程序和脚本，结束后按本文清理并断电。先读 [AGENTS.md](../AGENTS.md) 和[恢复说明](recovery.zh-CN.md)。

## 1. 准备环境，暂不连接相机

需要 Python 3.10+、Git 和 libusb。macOS 使用系统中的 libusb，Windows 按下节脚本准备环境与驱动；Linux 2.03 已有社区安装成功报告，具体范围见[验证说明](evidence.zh-CN.md#社区-linux-203-报告)。

### Windows 主机准备（PowerShell）

安装 Python 3.10+、Git，并确保 `py` 与 `git` 在 PATH 中。将两个配套仓库放在同一个父目录（`ZV-E10-5GHz-WiFi-Unlock` 和 `zv-e10-toolkit`），在 Wi-Fi 项目根目录运行；也可用 `-Toolkit` 指定 toolkit 的位置：

```powershell
git clone https://github.com/dino2048/zv-e10-toolkit.git ..\zv-e10-toolkit
git -C ..\zv-e10-toolkit checkout --detach a647c551f51f47ee28b5129b0f3c7f84fa3ad80b
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\setup-windows.ps1
$env:ZVE10_TOOLKIT = (Resolve-Path ..\zv-e10-toolkit).Path
$wifiPython = Join-Path $env:ZVE10_TOOLKIT 'linux\.venv\Scripts\python.exe'
& $wifiPython -B .\tools\check_offline.py
& $wifiPython -B -m unittest discover -s tools -p test_safety.py -v
```

已有 toolkit 目录时不要重复克隆或覆盖改动；先核对现有目录，再由 Agent 切换到上述固定提交。

准备脚本调用配套 toolkit 自己的 `linux/scripts/setup-windows.ps1`，由 toolkit 建立虚拟环境并固定 Sony-PMCA-RE 提交；不连接相机，也不修改 toolkit 源码。Windows 的 `chmod` 不控制目录访问权限，toolkit 用当前 Windows 用户的 SID 设置会话目录 ACL。私密会话仍应保存在本机可信磁盘。

下载依赖需要代理时，在命令后加 `-Proxy http://127.0.0.1:7897`（换成你自己的地址）。pip 默认不读取 `HTTP_PROXY`/`HTTPS_PROXY`；同一代理也会用于克隆 Sony-PMCA-RE。若代理下 pip 报 SSL 错误，先在新建的环境里升级 pip（`...\.venv\Scripts\python.exe -m pip install --upgrade pip`）：实测 Python 3.10 自带的 pip 23.0.1 在某个代理下失败，pip 26.3 正常。

USB 服务模式还需要检查驱动：Sony-PMCA-RE 的 Windows 流程要求分别给海量存储模式与服务模式安装 `libusb-win32` 驱动。用 [Zadig](https://zadig.akeo.ie/) 打开 Options → List All Devices，选中相机的 `054C:0D95` 存储接口安装 **libusb-win32**；相机切换到服务模式后，再给 `054C:0336` 装同一驱动。此后 Windows 不再把相机当作磁盘挂载；工具用完请在设备管理器恢复原驱动。若 Python 找不到已安装的驱动库，用 `LIBUSB0_PATH` 指向对应的 `libusb0.dll`。使用 libusb-win32 时不要设置 `ZVE10_LIBUSB1`；其他后端见 toolkit 说明。已验证的 Windows 会话在普通、非管理员 PowerShell 中运行；如果打开设备报 access denied，再用管理员 PowerShell 启动服务端。

Windows 2.03 的只读会话已验证（见证据记录）。对新电脑、新驱动或新相机，仍应先只读建会话、`inspect`、正常 `close`，核对 `loader_files_removed` 和 `service_returned` 后再考虑安装。

各主机统一使用 [zv-e10-toolkit `a647c55`](https://github.com/dino2048/zv-e10-toolkit/commit/a647c551f51f47ee28b5129b0f3c7f84fa3ad80b)，提供通用 Backup 操作、持久会话及 Windows 传输支持。macOS/Linux 克隆后切换到同一固定提交：

```sh
mkdir -p vendor
git clone https://github.com/dino2048/zv-e10-toolkit.git vendor/zv-e10-toolkit
export ZVE10_TOOLKIT="$PWD/vendor/zv-e10-toolkit"
git -C "$ZVE10_TOOLKIT" checkout --detach a647c551f51f47ee28b5129b0f3c7f84fa3ad80b
PYTHON=python3 sh "$ZVE10_TOOLKIT/linux/scripts/setup.sh"
export WIFI_PYTHON="$ZVE10_TOOLKIT/linux/.venv/bin/python"
"$WIFI_PYTHON" -B tools/wifi.py --help
```

已有更新版 toolkit 时，将 `ZVE10_TOOLKIT` 指向该目录，`WIFI_PYTHON` 指向其解释器即可，不必复制代码或重复建立环境。用户指定了解释器时优先使用。toolkit 的安装脚本负责依赖及固定版本 Sony-PMCA-RE；本项目不另存一套公共工具、依赖清单、服务端或客户端。Windows、macOS 和 Linux 使用同一固定 toolkit 提交。

仓库附带两个小型 ARM Linux 程序及汇编源码。`patch.arm` 就是历史实机成功使用的文件，MD5 为 `8a1bd57091f544a758300b7151d94f05`。`restore.arm` 使用相同源码反转原值和目标值构建，已用于 Windows 恢复/补丁往返。如需重建，使用支持 ARM 目标的 clang 和 GNU `arm-none-eabi-ld`：

```sh
PYTHON="$WIFI_PYTHON" sh tools/build-helpers.sh
```

无需 ARM libc。源码文件名或工具链变化可能改变 ELF 符号和元数据；应核对加载段及指令、数据，不能只比较文件大小。见[发布核查](release.zh-CN.md)。

## 2. 核对相机并备份

确认是 **ZV-E10 第一代，机内版本页显示 2.02 或 2.03**，供电稳定、正常启动，且没有尚未处理的旧修改。强烈建议用 USB-C 数据线连接相机和电脑，通过 [zv-e10-toolkit](https://github.com/dino2048/zv-e10-toolkit) 完整备份 eMMC 用户区并校验。备份可能包含设备秘密，应私密保管。写入前了解额外硬件 fastboot 恢复的途径；备份并不保证所有故障都能恢复。

将 USB 连接设为 **海量存储器（Mass Storage）**，使用支持数据传输的 USB-C 线。相机处于 USB 存储模式时可能无法操作菜单，应先建立持久服务会话，再请机主操作菜单。

机主需要明确确认实际使用国家或地区及修改范围。本文示例采用中国大陆 B=2/C=22；其他使用地按[地区配置](regions.zh-CN.md)选择并确认对应 B/C，写入与验收始终使用这组值。型号、固件、适用配置或目标文件不明时停止，不自动升级或降级固件。

## 3. 保持一个服务会话

在仓库根目录另开终端：

```sh
sudo /bin/launchctl asuser "$(id -u)" /usr/bin/env ZVE10_TOOLKIT="$ZVE10_TOOLKIT" "$WIFI_PYTHON" -B tools/wifi.py serve --client-uid "$(id -u)" --idle-timeout 3600 --session-dir private/install-01 --owner-authorized-write
```

每次使用新的会话目录，开始前确认没有其他服务连接。macOS 的已验证路径通过 sudo 取得权限，并用 launchctl asuser 保持用户服务上下文；Linux 去掉 `/bin/launchctl asuser "$(id -u)"`。使用正常的系统授权或终端输入，不要让 Agent 收集密码。会话在收到 `close` 或超过配置的空闲时间后结束；示例设置为操作完成后空闲一小时。toolkit 将队列及响应文件交回客户端 UID，必要时用 `--client-uid` 指定；Wi-Fi 快照归 toolkit 目录的所有者。只检查、不修改时，省略 `--owner-authorized-write`。

Windows 使用同一 PowerShell 终端启动服务端；不传 `--client-uid`，也不用 `sudo`。下例为已验证的 2.03 只读入口，已包含三个 Jiritsu 参数：

```powershell
$env:ZVE10_TOOLKIT = (Resolve-Path ..\zv-e10-toolkit).Path
$wifiPython = Join-Path $env:ZVE10_TOOLKIT 'linux\.venv\Scripts\python.exe'
& $wifiPython -B .\tools\wifi.py serve --backend jiritsu --firmware 2.03 --owner-authorized-exec --idle-timeout 3600 --session-dir private\win-inspect-01
```

另开 PowerShell 终端设置相同的 `ZVE10_TOOLKIT` 与 `$wifiPython`，等待 `private\win-inspect-01\state.json` 为 `ready`，然后请求 `inspect`。Windows PowerShell 5 向原生程序传 JSON 时会剥掉普通双引号，须保留反斜杠转义：`$request = '{\"action\":\"inspect\"}'`；`& $wifiPython -B .\tools\wifi.py request --session private\win-inspect-01 $request`。检查和备份期间保持这一个会话，不得在只读会话中执行 `patch`、`backup-write` 或 `wbi-drop`。

macOS/Linux 的 shell 示例使用 `private/install-01`；Windows 使用上面的 PowerShell 请求和 `private/win-inspect-01`。等待所选会话的 `state` 为 `ready`，两个终端保持相同环境。macOS/Linux 的检查命令为：

```sh
"$WIFI_PYTHON" -B tools/wifi.py request --session private/install-01 '{"action":"inspect"}'
```

`inspect` 会将完整目标库、两份 Backup 文件保存到私密会话目录，使用独立文件名避免覆盖，并返回三个属性值、挂载信息及快照编号。任何可能超过默认 360 秒的请求（例如服务端的 `raw-backup`）都要加 `--timeout 3600`。文件读取和终端操作共用同一个认证连接。认证本身可能更新 Sony 服务记账文件。

2.03 的 `inspect` 可选 `chunk_kib` 为 256、512、1024、2048 或 4096；大于 512 时自动使用并清理独立 RAM 缓冲。

原厂目标库长度必须为 **17,694,160 字节**，SHA-256 为：

```text
5ad8746a229da259fe00b297e8f897d682f7ae9a13393025b3d1c95a808e68d7
```

将返回的原始属性值、型号、机内版本、确认的地区、备份位置及文件哈希记入私密安装记录。文件已经是补丁版时，先检查是否已完成安装，不重复运行 `patch`。

### 写入前建议双遍备份（Windows 2.03）

只读服务端进入 `ready` 后，保持同一会话，在新建写入会话前先对用户区和 B0/B1 **各独立读取两遍**。电脑至少预留 5 GiB 可用空间。在第二个 PowerShell 终端执行：

```powershell
$request = '{\"action\":\"raw-backup\",\"passes\":2,\"chunk_kib\":4096}'
& $wifiPython -B .\tools\wifi.py request --session private\win-inspect-01 --timeout 7200 $request
```

私密保留两遍文件、`manifest.json` 和 `SHA256SUMS`。电脑独立重算每份保存文件的哈希并与清单比较，再审阅三个区域的 `comparisons`。`completed: true` 只代表读取完成，不保证用户区两遍完全相同；相机运行中可写数据可能变化。有差异时保留差异块清单，由 Agent 查清后再继续。


## 4. 执行已确认的最小修改

Wi-Fi 操作先检查 `/usr` 的挂载来源及整文件哈希，再通过一次 Jiritsu SET_FILE2 将固定哈希的小程序传到 `/tmp/jiritsu`，使用 toolkit 的 Jiritsu GET_FILE 完整读回并在主机逐字节核对；随后临时改为可写挂载，原位修改一个字节，导出完整结果，检查哈希和唯一差异，最后恢复只读挂载并删除临时程序。

```sh
"$WIFI_PYTHON" -B tools/wifi.py request --session private/install-01 '{"action":"patch"}'
```

Windows 先完成并校验备份。将 `$request` 设为 `'{\"action\":\"close\"}'`，用同一请求命令关闭只读会话；等 `closed`、`service_returned=true`、`loader_files_removed=true` 后，关机、等存取灯熄灭、拔 USB、取电池约 30 秒，再装电池开机并重新连接。机主确认写入范围后，新建写入会话：

```powershell
& $wifiPython -B .\tools\wifi.py serve --backend jiritsu --firmware 2.03 --owner-authorized-exec --owner-authorized-write --idle-timeout 3600 --session-dir private\win-install-01
```

等待该会话为 `ready`，先在其中重新执行 `inspect`，与预检保存的库哈希和属性原值比较，再发送补丁请求（保留反斜杠转义）：

```powershell
$request = '{\"action\":\"patch\"}'
& $wifiPython -B .\tools\wifi.py request --session private\win-install-01 $request
```

下面的 `backup-write` 请求同样处理。该步骤在 Windows 上做过往返验证，但**没有做原厂相机的首次安装验证**。

要求返回 `only_difference: 0xd778e4`，补丁后 SHA-256 为：

```text
14f42cc09ee1b9ddde5352482c13b68e5a5e97d9d79e8456087b5e0b7af6ff6a
```

再逐项写入 Backup 属性。**下例仅适用于检查到原值为 `00/09/09` 的情况；必须把 `expected` 换成本机实际保存的原值。** 所有值字符串均为十六进制。

```sh
"$WIFI_PYTHON" -B tools/wifi.py request --session private/install-01 '{"action":"backup-write","id":"0x01071C54","expected":"00","value":"01"}'
"$WIFI_PYTHON" -B tools/wifi.py request --session private/install-01 '{"action":"backup-write","id":"0x00A5000B","expected":"09","value":"02"}'
"$WIFI_PYTHON" -B tools/wifi.py request --session private/install-01 '{"action":"backup-write","id":"0x00A5000C","expected":"09","value":"16"}'
```

每条命令后检查 `match: true`。Wi-Fi 操作限制可修改的三个属性和值，再调用 toolkit 通用 Backup 接口：先保存原值，写入后调用 Sony 保存方法并立即读回。已经正确的属性可以跳过，不直接编辑 BK4 文件。若仅部分步骤成功，应保留每一步结果，按实际变化恢复。

结构化 Wi-Fi 或 Backup 操作报错会结束服务端。不要直接重发、重启或继续写入；先检查快照、状态和恢复说明。响应丢失不代表相机没有变化。恢复只读挂载失败时，必须先处理挂载状态，再考虑冷启动。

## 5. 验收并结束会话

再次执行 `inspect`，确认完整补丁哈希、菜单属性 `01` 和已选择的 B/C 值 和 `/usr` 只读。私密保留修改前后文件，然后执行：

```sh
"$WIFI_PYTHON" -B tools/wifi.py request --session private/install-01 '{"action":"close"}'
```

等待服务端退出，确认 state.json 中 `state: closed`、`service_returned: true`；Jiritsu 检查 `loader_files_removed: true`，旧终端检查 `terminal_closed: true`。收到 close 响应时，终端清理可能尚未结束，不能只看这一条响应。

相机 OFF，等待存取指示灯熄灭，拔掉 USB 并取下电池约 30 秒。重新装入后，在 `private/verify-01` 建立新的**只读**会话，等待 `ready` 再检查。保持会话打开，请机主进入“网络 → Wi-Fi 设置 → 频带”，检查 2.4/5 GHz 选择页。

**暖启动检查：**取电池约 30 秒仍可能从相机保存的 Warm Boot Image 恢复旧菜单状态。实机曾在补丁和三个属性都正确时，运行中的 Wi-Fi 页仍是 TypeRK 四项；内核日志有 `PM: Low-level resume complete`。在验收会话中查看启动日志，并核对当前 Page1 是否为 TypeNB 五项。若仍为 TypeRK 四项或缺少「频带」，停止验收，保留日志与快照；不要重刷同一字节、重复写 Backup 或把取电池当作已经完成真正冷启动。该机经先备份完整 60 MiB `nflasha5`、再用 Sony 原厂工具仅清除其首 512 B 暖镜像入口、断电重启后，日志无 `WARMBOOT` 行（内核的 `PM: Low-level resume` 和 `Waking up from system sleep` 在冷启动也会出现，不能单独作为暖启动证据），Page1 和屏幕均恢复五项。现已提供独立的 `wbi-prepare` / `wbi-drop` 保护流程，详见[暖镜像恢复](wbi.zh-CN.md)，必须完整双备份、另行确认 eMMC 写入并完整回读。Sony 原厂工具需从用户自备官方更新包私密提取，不随仓库分发。

在新建且处于 `ready` 状态的只读会话中执行：

```sh
"$WIFI_PYTHON" -B tools/wifi.py request --session private/verify-01 '{"action":"boot-check"}'
```

要求返回 `page1.type: TypeNB`、`page1.count: 5`，并由机主确认原生频带页能打开。`boot-check` 读取全局 Page1 对象；最终仍以相机屏幕验证。若补丁及属性正确但返回 TypeRK/4，请在 Agent 协助下按[暖镜像恢复流程](wbi.zh-CN.md)处理。WBI 失效是单独确认的 eMMC 操作，不能自动接在补丁之后执行。

需要功能检查或活动无线状态采样时，按[验收与恢复](recovery.zh-CN.md)执行。完成后正常关闭验收会话，所有个人备份均不得混入公开发布包。


更新后的暖镜像也可以恢复已解锁的五项菜单。菜单、文件和属性正确时，仅有暖恢复日志不是重复执行 WBI 的理由。


重建结果保存在忽略的 tools/build/ 中，自动与正式助手的 ELF 执行段比较，不覆盖固定哈希的运行文件。
