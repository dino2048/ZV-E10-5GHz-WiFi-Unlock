# 版本差异与验证结果

**简体中文** | [English](evidence.md)

原生频段菜单已在第一代 ZV-E10 的 2.02、2.03 上验证。两个系统使用相同的一字节和三个属性修改，服务连接方式不同。

## Windows 2.03

测试环境为 Windows 10、libusb-win32 驱动和普通 PowerShell，使用配套 toolkit 的持久 Jiritsu 会话。

| 操作 | 验证结果 |
| --- | --- |
| 环境准备与连接 | 安装脚本、版本核对、持久服务会话可用 |
| 完整库读取 | 17,694,160 字节，分块哈希及保存文件完整哈希一致 |
| 原始备份 | 用户区与 B0/B1 共 1,962,934,272 字节，接收和保存文件校验通过 |
| Backup 属性 | 三个属性均完成真实改值、保存、读回及恢复 |
| 菜单库补丁与恢复 | `restore` → `patch` 往返，每次完整哈希正确，唯一差异为 `0xD778E4`，结束时 `/usr` 只读 |
| WBI 查询 | 完整分区只读查询可用 |
| 正常关闭 | 临时加载文件清理、服务退出确认通过 |

属性往返为 `01→00→01`、`02→01→02`、`16→15→16`。测试结束时库与属性恢复到测试前状态。Windows 原厂首次完整安装和 WBI 失效写入尚待实机确认；WBI 处理的底层流程已有 macOS 实机记录。

Windows 使用按响应长度读取的服务传输，避免 Sony-PMCA-RE 的额外收尾读取；实现位于 toolkit 的 `linux/host/zve10_senser.py`。原始备份速度约 2.04 MiB/s；更多备份配置和测量见 [toolkit](https://github.com/dino2048/zv-e10-toolkit)。

## 社区 Linux 2.03 报告

[Issue #2](https://github.com/dino2048/ZV-E10-5GHz-WiFi-Unlock/issues/2) 报告一台 ZV-E10 2.03 在 Linux x86_64 上完成备份、补丁、三个属性、WBI 失效和重新开机验收。使用 KR2/CEC 类 `B=14/C=23`（`01/0E/17`），实际使用地为尼泊尔；报告称菜单为 TypeNB 五项，可选择 5 GHz，热点活动配置读到 XR/88。

这是社区单机报告，维护者尚未取得并独立复核完整记录。对方为绕过旧版中国属性检查做过本地修改；不能据此宣称未修改的旧版工具已直接完成该流程。手机传图、路由器侧 XR/144、功率及 DFS 行为没有验收。当前版本已取消 WBI 对地区值的固定要求，改为保存并核对当前属性；这项新代码经过离线测试。

## 版本对照

| 项目 | 2.02 | 2.03 |
| --- | --- | --- |
| 系统标识 | `30110_05.2025031501` | `30110_06.2026060501` |
| root 会话 | 原终端后端 | Jiritsu 后端，启动时加 `--backend jiritsu --firmware 2.03 --owner-authorized-exec` |
| 备份传输 | FileControl 直接连续读取 | root 读入 RAM 文件，再通过 Jiritsu 下载 |
| 完整备份记录 | 用户区与 B0/B1 双遍读取；另有 fastboot 双备份 | 用户区与 B0/B1 完整单遍，逐块及主机完整重读校验通过 |
| 备份速度 | Linux FileControl 路线约 12 MiB/s | 512 KiB 中转约 1.3 MiB/s；独立 RAM 大缓冲完整单遍为 1.989 MiB/s |
| Wi-Fi 修改 | 相同的一字节与三个 Backup 属性 | 相同的一字节与三个 Backup 属性 |
| WBI 处理 | 完整双备份、执行 Sony 工具、完整写后比较 | 同一流程；按 2.03 的系统指纹识别 |
| 原生频段菜单 | TypeNB 五项，2.4/5 GHz 菜单可用 | TypeNB 五项，2.4/5 GHz 菜单可用 |

Jiritsu 的“持续会话”指命令保留同一个 shell 的状态，不是重启后自动 root。本机 2.03 的旧终端路径失败，FileControl 返回 `0x80`、无数据，因此使用 Jiritsu；不能据此推断所有相机都删除了该协议。两个版本的 `libObj.so` 不同，WBI 工具分别核对对应指纹。

## 共同配置与修改验证

实测主机为 macOS，通过 USB-C 连接；使用地区为中国大陆，B=2/C=22，对应热点 XR/76、路由器 XR/143。

- `CautionConfig.so` 长度：17,694,160 字节，两个版本的目标原版库一致。
- 原版 SHA-256：`5ad8746a229da259fe00b297e8f897d682f7ae9a13393025b3d1c95a808e68d7`。
- 修改后 SHA-256：`14f42cc09ee1b9ddde5352482c13b68e5a5e97d9d79e8456087b5e0b7af6ff6a`。
- 完整文件只差一字节：偏移 `0xD778E4`，`20 → 1B`，原位写入并保留文件长度。
- Backup 属性保存并读回一致：`0x01071C54=01`、`0x00A5000B=02`、`0x00A5000C=16`（十六进制 16 为十进制 22）。
- 重启后修改保留，`/usr` 恢复只读，上传的辅助文件清理完成。

暖恢复可能沿用旧的 TypeRK 四项菜单。两个版本均通过[WBI 流程](wbi.zh-CN.md)保存两份相同的完整 60 MiB 原始镜像、写前再核对，运行同一个 Sony 工具后完整读回。输出为 `[UD_WBI_DROP] /dev/nflasha5 wbi_drop`；逐字节确认只有首 512 字节清零，其余不变，重启后原生菜单可用。

## 无线功能记录

2.02 已实测 5 GHz 手机传图及经 5 GHz 路由器远程拍摄、接收照片。活动驱动读到热点 XR/76、路由器 XR/143；热点曾使用 5 GHz 信道 157/80 MHz，路由器曾使用信道 40/80 MHz。2.03 的记录覆盖文件/属性保留、WBI 处理及运行中的 TypeNB 五项菜单。功能记录按实际测试版本归属，不混用结果。

## 2.03 完整备份

独立 8 MiB tmpfs、4 MiB 分块已完整读取：

| 区域 | 字节数 |
| --- | ---: |
| Linux 可见用户区（含间隙与尾部） | 1,954,545,664 |
| B0 启动区 | 4,194,304 |
| B1 启动区 | 4,194,304 |
| 合计 | 1,962,934,272 |

每块相机/主机 SHA-256 一致，三个保存文件经电脑完整重读校验。备份动作耗时 **940.956 秒，平均 1.989 MiB/s**，包含前置检查、元数据、保存校验及 RAM 挂载清理，不含 USB 会话建立和管理员等待；整个读取没有断联。

正式 toolkit raw-backup 动作支持 chunk_kib=4096 自动管理独立大缓冲；省略时默认 512 KiB。单遍运行中读取与独立双遍、原子快照、恢复验证是不同项目。备份范围不含 RPMB、OTP/eFuse 或隐藏区域。

短读取消也已验证：保留未完成文件和取消清单，电脑重读一致，取消后连接可继续使用。结束时独立 RAM 挂载已卸载、挂载点删除，加载文件已确认移除，服务正常返回；最后由机主断电结束剩余 RAM shell。

## 发布工具与可复核信息

安装器复用 toolkit 的持久会话、传输及通用 Backup 接口。版本识别、哈希保护、上传读回、WBI 执行保护等有离线测试；实机记录对应上文各项操作。具体代码检查见 [offline-checks.json](offline-checks.json)，Agent 操作要求见 [AGENTS.md](../AGENTS.md)。

只使用原位单字节写入，不用整文件 cp 或会截断库的 dd 写法。每次安装保存机主自己的原文件、属性与 WBI 备份，不能用其他相机的数据代替。完整文件指纹与技术依据见[技术说明](technical.zh-CN.md)，恢复步骤见[恢复说明](recovery.zh-CN.md)。

Sony WBI 工具由用户自备的官方 2.03 更新包离线提取，包版本不限制相机只能是 2.03；两个已知系统使用同一精确哈希工具。仓库不分发 Sony 固件、工具、相机镜像、密钥或私密会话。

## 资料来源

- [Sony A7C 频带设置](https://helpguide.sony.net/ilc/2020/v1/en/contents/TP1000156044.html)：原生菜单及直连功能适用范围。
- [Sony A7C 访问点设置](https://helpguide.sony.net/ilc/2020/v1/en/contents/TP1000115299.html)：连接路由器的操作。
- [Sony ZV-E10 PC Remote](https://helpguide.sony.net/ilc/2070/v1/en/contents/TP0002392805.html)：直连、访问点连接、配对、拍摄及保存方式。
- [Sony A7C 规格](https://helpguide.sony.net/ilc/2020/v1/en/contents/TP1000156734.html)：不同地区无线版本。
- [IFT Sony 设备清单](https://www.ift.org.mx/node/19562)：ZV-E10 Type1DR 条目。
- [NTC 2021 设备清单](https://region7.ntc.gov.ph/wp-content/uploads/2024/01/RCE_08312021.pdf)：A7C Type1DR 条目，印刷第 187 页。
- [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE)、[MIT 许可](https://github.com/ma1co/Sony-PMCA-RE/blob/master/LICENSE.txt)：服务协议实现；toolkit 固定版本为 `a82f5baaa8e9c3d9f28f94699e860fb2e48cc8e0`。
- [zv-e10-toolkit](https://github.com/dino2048/zv-e10-toolkit)：备份、持久服务及恢复工具。使用配套、包含 Windows 安装与服务响应支持的 toolkit。
