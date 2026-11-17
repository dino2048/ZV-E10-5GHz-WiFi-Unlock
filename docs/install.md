# Agent-assisted installation

**English** | [简体中文](install.zh-CN.md)

Follow this guide with an AI Agent, using the companion toolkit for connection, backup and modification. The Windows instructions target first-generation ZV-E10 system 2.03; see [validation](evidence.md) for platform coverage.

Every server command for system 2.03 needs `--backend jiritsu --firmware 2.03 --owner-authorized-exec`. Jiritsu temporarily uploads a loader and script; finish with the documented cleanup and power removal. Read [AGENTS.md](../AGENTS.md) and [recovery](recovery.md) first.

Use the latest `main` of [zv-e10-toolkit](https://github.com/dino2048/zv-e10-toolkit). Its Jiritsu startup prepares the service workspace with the camera's own MOUNT command before checking old loader files or uploading. If initialization fails with `0x10000004`, stop and preserve the error; it can have causes other than a missing directory. Resolution on the community camera reporting this error remains unconfirmed.

## 1. Prepare without connecting

Use Python 3.10+, Git and libusb. On macOS use the installed libusb; on Windows follow the setup and driver steps below. Linux 2.03 has a community installation report; see [validation](evidence.md#community-linux-203-report) for its scope.

### Windows host preparation (PowerShell)

Install Python 3.10+ and Git, with `py` and `git` on PATH. Place the companion `ZV-E10-5GHz-WiFi-Unlock` and `zv-e10-toolkit` checkouts beside each other, then run from the Wi-Fi repository root. Pass `-Toolkit` to use another toolkit path:

```powershell
git clone --branch main https://github.com/dino2048/zv-e10-toolkit.git ..\zv-e10-toolkit
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\setup-windows.ps1
$env:ZVE10_TOOLKIT = (Resolve-Path ..\zv-e10-toolkit).Path
$wifiPython = Join-Path $env:ZVE10_TOOLKIT 'linux\.venv\Scripts\python.exe'
& $wifiPython -B .\tools\check_offline.py
& $wifiPython -B -m unittest discover -s tools -p test_safety.py -v
```

If the toolkit directory already exists, preserve and review local changes; do not clone over it. Before opening a camera session, update a clean checkout with `git -C ..\zv-e10-toolkit switch main` followed by `git -C ..\zv-e10-toolkit pull --ff-only origin main`. If either command fails, resolve it before continuing; do not discard local changes. Rerun setup and the offline checks after updating. Keep the checkout unchanged throughout a camera session.

The script calls the companion toolkit's own `linux/scripts/setup-windows.ps1`, which prepares its virtual environment and pins Sony-PMCA-RE. It neither connects to the camera nor patches toolkit source. On Windows, `chmod` does not restrict directory access, so the toolkit sets the session directory ACL to the current user's SID. Keep private sessions on a trusted local disk.

When dependency downloads need a proxy, add `-Proxy http://127.0.0.1:7897` (use your own address). pip ignores `HTTP_PROXY`/`HTTPS_PROXY` by design; the same proxy is passed to the Sony-PMCA-RE clone. If pip reports an SSL error through a proxy, upgrade pip inside the new environment first (`...\.venv\Scripts\python.exe -m pip install --upgrade pip`): the pip 23.0.1 bundled with Python 3.10 failed through one tested proxy, while pip 26.3 worked.

Sony-PMCA-RE's Windows service-mode instructions require a `libusb-win32` driver for both the mass-storage and service-mode device. With [Zadig](https://zadig.akeo.ie/), enable Options → List All Devices, select the camera's `054C:0D95` storage interface, and install **libusb-win32**; once the camera switches to service mode, install the same driver for `054C:0336`. Windows then stops mounting the camera as a drive; restore the original driver in Device Manager when the tools are no longer needed. If Python cannot locate the installed driver library, set `LIBUSB0_PATH` to its `libusb0.dll` path. Leave `ZVE10_LIBUSB1` unset for libusb-win32; see the toolkit guide for other driver backends. The validated Windows session ran in a normal, non-elevated PowerShell; if opening the device reports access denied, run the server from an elevated PowerShell.

A Windows 2.03 read-only session has been validated (see the evidence record). For a new host, driver setup or camera, still start with a read-only session, run `inspect`, close normally and check `loader_files_removed` and `service_returned` before any installation.

All hosts use the latest toolkit `main`, which provides shared Backup actions, the persistent session, Windows transport and service-workspace initialization. On macOS/Linux:

```sh
mkdir -p vendor
git clone --branch main https://github.com/dino2048/zv-e10-toolkit.git vendor/zv-e10-toolkit
export ZVE10_TOOLKIT="$PWD/vendor/zv-e10-toolkit"
PYTHON=python3 sh "$ZVE10_TOOLKIT/linux/scripts/setup.sh"
export WIFI_PYTHON="$ZVE10_TOOLKIT/linux/.venv/bin/python"
"$WIFI_PYTHON" -B tools/wifi.py --help
```

If you already have the toolkit, set `ZVE10_TOOLKIT` to that checkout and `WIFI_PYTHON` to its interpreter; do not copy its code or create another environment unnecessarily. Review local changes, then update a clean checkout before connecting:

```sh
git -C "$ZVE10_TOOLKIT" switch main
git -C "$ZVE10_TOOLKIT" pull --ff-only origin main
PYTHON=python3 sh "$ZVE10_TOOLKIT/linux/scripts/setup.sh"
```

Stop if switching or updating fails; preserve local changes and resolve the problem first. Run the [offline checks](release.md#checks-without-a-camera) after updating, and keep the checkout unchanged throughout a camera session. Use the owner's chosen interpreter when specified. Toolkit setup installs dependencies and its pinned Sony-PMCA-RE checkout. This repository does not carry duplicate common helpers, dependency lists, service servers or clients.

The two tiny ARM Linux helpers are supplied with assembly source. `patch.arm` is the exact camera-tested executable (MD5 `8a1bd57091f544a758300b7151d94f05`). `restore.arm` is built from the same source with expected/replacement bytes reversed and was exercised in the Windows restore/patch round trip. To rebuild, use clang with an ARM target and GNU `arm-none-eabi-ld`:

```sh
PYTHON="$WIFI_PYTHON" sh tools/build-helpers.sh
```

The build writes to ignored tools/build/ and checks both ELF load segments against the shipped helpers; it never overwrites the hash-pinned runtime files. No ARM libc is required. A different source filename/toolchain may change ELF symbols or metadata; validate load segments and instruction/data content, not just executable size. See [release checks](release.md).

## 2. Confirm the camera and backup

Confirm **ZV-E10 first generation, displayed firmware 2.02 or 2.03**, stable power, normal boot and no unresolved prior modifications. Strongly recommend a verified full eMMC user-area backup via [zv-e10-toolkit](https://github.com/dino2048/zv-e10-toolkit), over ordinary USB-C. Keep the backup privately; it may contain device secrets. Know where a hardware-assisted fastboot recovery would come from before writing. Backup is not a guarantee of recovery.

Set USB Connection to **Mass Storage**, not Auto/MTP, and use a data-capable USB-C cable. Do not ask the owner to navigate menus while stuck in USB storage: start the persistent service session first.

The owner must explicitly confirm the country of use and the proposed changes. The examples use China B=2/C=22. For another country, select and confirm the B/C pair using [region profiles](regions.md) and use it consistently in writing and acceptance. Stop if the appropriate configuration, firmware or library content cannot be established. Do not automatically upgrade/downgrade firmware.

## 3. Keep one service session open

From the repository root, in a separate terminal:

```sh
sudo /bin/launchctl asuser "$(id -u)" /usr/bin/env ZVE10_TOOLKIT="$ZVE10_TOOLKIT" "$WIFI_PYTHON" -B tools/wifi.py serve --client-uid "$(id -u)" --idle-timeout 3600 --session-dir private/install-01 --owner-authorized-write
```

Use a new directory for every session; resolve any prior session before starting another. `sudo` grants raw USB access; `launchctl asuser` keeps the macOS user-service context, as in the validated launcher. On Linux omit `/bin/launchctl asuser "$(id -u)"`; use the host's normal privileged terminal mechanism, never ask an agent to collect a password. The toolkit session stays open until `close` or the configured idle timeout after the last completed operation (one hour in the example). The existing toolkit server hands its queue/results back to the client UID; `--client-uid` can specify the owner when needed. Wi-Fi snapshots use the toolkit checkout owner. Only run trusted code as root. For inspection only, omit `--owner-authorized-write`.

On Windows, start the server in PowerShell without `sudo` or `--client-uid`. The read-only example below targets the validated system 2.03 and includes its Jiritsu arguments.

```powershell
$env:ZVE10_TOOLKIT = (Resolve-Path ..\zv-e10-toolkit).Path
$wifiPython = Join-Path $env:ZVE10_TOOLKIT 'linux\.venv\Scripts\python.exe'
& $wifiPython -B .\tools\wifi.py serve --backend jiritsu --firmware 2.03 --owner-authorized-exec --idle-timeout 3600 --session-dir private\win-inspect-01
```

In another PowerShell terminal, set the same environment and interpreter and wait for `private\win-inspect-01\state.json` to say `ready`. Windows PowerShell 5 strips plain double quotes in native-program arguments, so preserve the backslashes: run `$request = '{\"action\":\"inspect\"}'` and `& $wifiPython -B .\tools\wifi.py request --session private\win-inspect-01 $request`. Keep this session open through inspection and backup. Do not run `patch`, `backup-write`, or `wbi-drop` in this read-only session.

For macOS/Linux, the shell examples use `private/install-01`; Windows uses the PowerShell requests and `private/win-inspect-01` above. Wait for the selected session's `state: ready` and keep the same environment in both terminals. The macOS/Linux inspection request is:

```sh
"$WIFI_PYTHON" -B tools/wifi.py request --session private/install-01 '{"action":"inspect"}'
```

This exports the full current library and both Backup files to unique names inside the private session directory, reports the three one-byte values and mounts. Record the snapshot token. Add `--timeout 3600` to any request that can run longer than the default 360 seconds, such as the server's `raw-backup` action. FileControl reads and the terminal share this same authenticated service connection. Authentication itself may update Sony service bookkeeping; read-only inspection is not a promise of zero internal bookkeeping.

For system 2.03, `inspect` accepts `chunk_kib` values 256, 512, 1024, 2048 or 4096. Values above 512 automatically use and clean a dedicated RAM buffer.

Require factory library size 17,694,160 and SHA-256:

```text
5ad8746a229da259fe00b297e8f897d682f7ae9a13393025b3d1c95a808e68d7
```

Preserve the returned original property values in a private installation note, alongside the model, displayed firmware, confirmed region, backup location, and file hashes. If the library is already patched, inspect all state and decide whether installation is already complete; do not rerun `patch`.

### Recommended backup before writing (Windows 2.03)

After the read-only server reaches `ready`, keep that same session open and request **two independent reads** of the user area and B0/B1 before starting a write session. Allow at least 5 GiB free host disk space. In the second PowerShell terminal:

```powershell
$request = '{\"action\":\"raw-backup\",\"passes\":2,\"chunk_kib\":4096}'
& $wifiPython -B .\tools\wifi.py request --session private\win-inspect-01 --timeout 7200 $request
```

Keep both passes, `manifest.json` and `SHA256SUMS` privately. Independently hash each saved file and compare it with the manifest, then review `comparisons` for all three regions. `completed: true` means the reads finished; it does not guarantee that both user-area passes are identical. A running camera may change writable data between passes. If they differ, preserve the differing-chunk list and have the Agent investigate before proceeding.


## 4. Perform the confirmed minimal changes

The Wi-Fi action guards `/usr` mount identity and full library hash, uploads the hash-pinned helper in one Jiritsu SET_FILE2 write under `/tmp/jiritsu`, reads the whole file through toolkit Jiritsu GET_FILE and compares every byte on the host, remounts `/usr` writable, runs the non-truncating writer, exports the result, validates the complete expected hash and unique difference, then remounts read-only and removes the helper.

```sh
"$WIFI_PYTHON" -B tools/wifi.py request --session private/install-01 '{"action":"patch"}'
```

On Windows, finish and verify the backup first. Close the read-only session with `$request = '{\"action\":\"close\"}'` and the same request command. Wait for `closed`, `service_returned=true` and `loader_files_removed=true`, then switch OFF, wait for the access lamp, unplug USB and remove the battery for about 30 seconds. Refit the battery, power on and reconnect. After the owner confirms the write scope, start a new write session:

```powershell
& $wifiPython -B .\tools\wifi.py serve --backend jiritsu --firmware 2.03 --owner-authorized-exec --owner-authorized-write --idle-timeout 3600 --session-dir private\win-install-01
```

Wait for this session to become `ready`. Run `inspect` in it again and compare the library hash and original properties with the saved preflight results. Only then send the patch request, keeping the backslash escapes:

```powershell
$request = '{\"action\":\"patch\"}'
& $wifiPython -B .\tools\wifi.py request --session private\win-install-01 $request
```

The `backup-write` requests below use the same form. The Windows round trip of this phase is validated; a first-time installation on Windows has not been tested.

Require `only_difference: 0xd778e4` and patched SHA-256:

```text
14f42cc09ee1b9ddde5352482c13b68e5a5e97d9d79e8456087b5e0b7af6ff6a
```

Then write the Backup properties individually. **These examples assume the inspected originals were `00/09/09`; replace `expected` with your own saved originals.** All value strings are hexadecimal. Never copy these defaults without inspection.

```sh
"$WIFI_PYTHON" -B tools/wifi.py request --session private/install-01 '{"action":"backup-write","id":"0x01071C54","expected":"00","value":"01"}'
"$WIFI_PYTHON" -B tools/wifi.py request --session private/install-01 '{"action":"backup-write","id":"0x00A5000B","expected":"09","value":"02"}'
"$WIFI_PYTHON" -B tools/wifi.py request --session private/install-01 '{"action":"backup-write","id":"0x00A5000C","expected":"09","value":"16"}'
```

Review `match: true` after each command. The Wi-Fi action validates the three permitted keys and values, then delegates to toolkit's generic Backup action, which saves the original before writing, invokes Sony's save call, and immediately rereads it. Already-correct properties can be skipped. It does not edit the BK4 files directly. Partial completion is possible: retain each result and restore only what changed if needed.

An error in a structured Wi-Fi/Backup action stops the existing server. Do not blindly resend, reboot, or continue. Check preserved snapshots, state, and the recovery guide. A failed response after writing may still mean the camera changed. A remount failure requires resolving the current mount state before cold boot.

## 5. Verify and close

Run `inspect` again. Require the patched full hash, the menu property `01` and the selected B/C values, and `/usr` mounted read-only. Preserve before/after files privately. Then:

```sh
"$WIFI_PYTHON" -B tools/wifi.py request --session private/install-01 '{"action":"close"}'
```

Wait for server exit and require `state: closed`, `service_returned: true`, and `loader_files_removed: true` for Jiritsu or `terminal_closed: true` for the legacy terminal in state.json. The close response alone precedes terminal teardown and is not sufficient.

Switch OFF, wait for the access lamp to go out, unplug USB and remove the battery for about 30 seconds. Refit it and start a new **read-only** session in `private/verify-01`, wait for `ready`, then inspect. Ask the owner to check Network → Wi-Fi Settings → Frequency Band and select 2.4/5 GHz while the session remains ready/open.

**Warm boot check:** Battery removal for about 30 seconds may still resume a saved Warm Boot Image with an old four-item Wi-Fi page. In the verification session, inspect the boot log and confirm that the running Page1 has five TypeNB items. If it is still TypeRK/four items or the band menu is missing, stop acceptance and preserve the logs and snapshot. Do not repeat the same byte patch or Backup writes. On the tested camera, a separately backed-up, verified Sony updater operation invalidated only the first 512 bytes of the 60 MiB `nflasha5` warm image; the next boot had no `WARMBOOT` line (the kernel's `PM: Low-level resume` and `Waking up from system sleep` lines also appear on cold boots) and restored the five-item native page. Use the separate guarded `wbi-prepare` / `wbi-drop` actions in [WBI recovery](wbi.md), with full double backup, explicit eMMC-write consent and readback. Sony's binary must be extracted privately from the owner's official update package; it is not distributed here.

Run the read-only check in the new ready session:

```sh
"$WIFI_PYTHON" -B tools/wifi.py request --session private/verify-01 '{"action":"boot-check"}'
```

Require `page1.type: TypeNB`, `page1.count: 5`, the owner's confirmation that the native band page opens. `boot-check` reads the global Page1 object; the camera menu remains the final UI check. If the result is TypeRK/four items while the patch and properties match, follow [WBI recovery](wbi.md) under Agent supervision. WBI invalidation is a separate confirmed eMMC operation; it is never automatically chained to the patch.

Use [verification steps](recovery.md) for optional functional checks and read-only active radio sampling. Close the verification session normally. Keep all private backups outside any public archive.


An updated warm image can also restore the unlocked five-item menu. Warm-resume logs alone do not justify repeating WBI invalidation when menu, file and properties are correct.
