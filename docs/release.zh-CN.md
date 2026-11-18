# 许可与验证范围

**简体中文** | [English](release.md)

## 许可边界

- 本项目原创代码、辅助程序汇编及文档采用 MIT，见 [LICENSE](../LICENSE)。
- 服务端、客户端、请求队列、认证及通用 Backup 操作由外部 [zv-e10-toolkit](https://github.com/dino2048/zv-e10-toolkit) 提供。本仓库只保留 Wi-Fi 专用规则及补丁操作，没有复制 toolkit 的通用实现；保留 [toolkit MIT 声明](../licenses/zv-e10-toolkit-MIT.txt)用于署名。
- Sony-PMCA-RE 为外部运行依赖，未随仓库打包；保留其 [MIT 声明](../licenses/Sony-PMCA-RE-MIT.txt)。下载依赖各自保留原许可证，重新分发环境时应保留相关声明。本项目不分发 Python 环境、libusb、clang 或 GNU binutils。
- OpenWrt `bcmclm.c` 为 GPL-2.0-or-later，仅作技术文档中的研究参考，本仓库未复制其实现。
- `patch.arm`、`restore.arm` 是自有的小型 ARM Linux 程序，不是 Sony 固件，均附汇编源码。
- Sony 完整固件、专有库、驱动、NVRAM／校准数据、个人备份、设备密钥和凭据未包含在仓库中，也不属于本项目许可范围。公开哈希及偏移不授予再分发 Sony 代码的权利。Sony 及产品名称归相应权利人。

## 验证范围

菜单解锁、属性及文件修改、WBI 处理、无线功能的系统与平台范围见[验证说明](evidence.zh-CN.md)。Windows 2.03 已有社区完整安装报告，包含工具提取、WBI 写入、重启验收及手机连接 5 GHz 热点。

配套使用 [zv-e10-toolkit 最新 `main`](https://github.com/dino2048/zv-e10-toolkit/tree/main)，包含 Windows 支持及 Jiritsu 工作区初始化。连接前更新并重跑离线检查，相机会话期间保持代码不变。[offline-checks.json](offline-checks.json) 记录验证时实际使用的 toolkit 提交，仅供追溯，不限制安装版本，也不表示未来更新已经通过验证。

## 不连接相机的自检

按[安装说明](install.zh-CN.md)准备环境并设置变量后，在本仓库执行：

```sh
"$WIFI_PYTHON" -B tools/check_offline.py
"$WIFI_PYTHON" -B -m unittest discover -s tools -p test_safety.py -v
"$WIFI_PYTHON" -B -m unittest discover -s "$ZVE10_TOOLKIT/linux/tests" -v
"$WIFI_PYTHON" -B "$ZVE10_TOOLKIT/linux/host/zve10_terminal_server.py" --self-test
```

这些检查不连接相机，也不要求个人固件文件。维护者可用 `check_offline.py` 的 `--factory`、`--patched`、`--tested-helper` 参数，对私密样本做额外比对；样本不应加入仓库。

## 分享文件时

不要把 `private/`、`vendor/`、虚拟环境或外部相机备份加入公开压缩包。`.gitignore` 只影响 Git 文件跟踪，不会自动排除任意方式打包的内容。私密快照可能含设备标识、凭据或密钥。

两个固件版本的实机结果、连接和备份差异统一见[验证说明](evidence.zh-CN.md)；离线检查项目单独记录在 [offline-checks.json](offline-checks.json)。
