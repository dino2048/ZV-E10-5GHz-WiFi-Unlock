# Licensing and validation scope

**English** | [简体中文](release.zh-CN.md)

## License boundaries

- Original project code, helper assembly and documentation are MIT licensed; see [LICENSE](../LICENSE).
- Service server/client, queue, authentication and generic Backup actions come from external [zv-e10-toolkit](https://github.com/dino2048/zv-e10-toolkit). This repository keeps only Wi-Fi-specific rules and patch operations, without copying toolkit implementations. Its [MIT notice](../licenses/zv-e10-toolkit-MIT.txt) is retained for attribution.
- Sony-PMCA-RE is an external runtime dependency, not bundled; its [MIT notice](../licenses/Sony-PMCA-RE-MIT.txt) is retained. Downloaded dependencies retain their own licenses and notices when redistributing an environment. No Python environment, libusb, clang or GNU binutils is distributed here.
- OpenWrt `bcmclm.c` is GPL-2.0-or-later and is only a technical research reference; no implementation is copied here.
- `patch.arm` and `restore.arm` are our small ARM Linux programs, not Sony firmware. Both have assembly source.
- Sony firmware, proprietary libraries, driver, NVRAM/calibration, personal backups, device keys and credentials are not included or licensed by this project. Published hashes and offsets do not grant permission to redistribute Sony code. Sony and product names belong to their owners.

## Validation scope

See [validation](evidence.md) for system and platform coverage of menu unlocking, property/file changes, WBI handling and wireless functions. Windows 2.03 has a community complete-installation report including tool extraction, WBI writing, restart acceptance and a phone connection to the 5 GHz hotspot.

Use the latest [zv-e10-toolkit `main`](https://github.com/dino2048/zv-e10-toolkit/tree/main), including Windows support and Jiritsu workspace initialization. Update before connecting, rerun the offline checks, and keep the checkout unchanged during a camera session. [offline-checks.json](offline-checks.json) records the exact toolkit revision used for validation; it is evidence, not an installation pin or a claim that future revisions have already been tested.

## Checks without a camera

After preparing the environment and variables in [installation](install.md), run from this repository:

```sh
"$WIFI_PYTHON" -B tools/check_offline.py
"$WIFI_PYTHON" -B -m unittest discover -s tools -p test_safety.py -v
"$WIFI_PYTHON" -B -m unittest discover -s "$ZVE10_TOOLKIT/linux/tests" -v
"$WIFI_PYTHON" -B "$ZVE10_TOOLKIT/linux/host/zve10_terminal_server.py" --self-test
```

These checks neither connect to a camera nor require private firmware files. Maintainers may use `check_offline.py` options `--factory`, `--patched` and `--tested-helper` for extra comparison against private evidence; do not add those fixtures to the repository.

## Sharing files

Exclude `private/`, `vendor/`, virtual environments and external camera backups from public archives. `.gitignore` controls Git tracking and does not protect arbitrary zip operations. Private snapshots may contain device identifiers, credentials or keys.

See [firmware differences and validation results](evidence.md) for both versions; offline checks are recorded separately in [offline-checks.json](offline-checks.json).
