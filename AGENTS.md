# AI agent entry point

## Public publication content

This is an independent public release repository under `publish/`. Write README and installation pages for external users, with the language switch immediately after the title. Keep Agent rules here and build/test details in release documentation. Keep local handoffs, session identifiers, deleted-file stories and pending-commit notes outside the public repository. Put measured evidence and material validation boundaries in docs/evidence.md, without duplicating experiment history throughout user instructions. Recommend two-pass backups and saved-file verification; never describe an unperformed test as passed. Keep Chinese and English pages aligned.

Read README.md, docs/install.md, docs/regions.md, docs/recovery.md, and docs/release.md before device access. Do not rely on earlier chat history. Explain results in the owner's language. Use docs/evidence.md for hardware and offline validation scope.

## Scope and permission

- Accept only first-generation ZV-E10 known systems 2.02 (`30110_05.2025031501`) and 2.03 (`30110_06.2026060501`), with two exact matching reads. For 2.03 require `--backend jiritsu --firmware 2.03 --owner-authorized-exec` on the toolkit server. Full single-pass backup and menu/WBI evidence are recorded for 2.03; do not claim hotspot/router functional validation. Unknown model/version must stop.
- First inventory USB connection, boot status, power, backup availability, existing modifications, and host dependencies. Strongly recommend and help verify an eMMC user-area backup with zv-e10-toolkit. Obtain explicit acknowledgement if the owner chooses to proceed without it; never imply that file snapshots replace it.
- Ask the owner for the actual country/region of operation and explicit confirmation of the B/C choice and scope: one file byte, three Backup properties, temporary helper upload and `/usr` remount. Never infer region. Choose B/C using docs/regions.md and the owner-confirmed country, without silently substituting another region. China B=2/C=22 has maintainer functional evidence; B=14/C=23 has a community Linux 2.03 installation/menu/hotspot-profile report, not complete transfer/router validation. Do not treat a reference template as a tested result.
- Do not connect or modify a camera when the current task is only document review or packaging. Do not publish, upload, or push without a publication request.

## Exact implementation

Use tools/wifi.py, not newly guessed offsets, raw partition writes, whole-file copies, or ad-hoc Backup database editing. It imports zv-e10-toolkit's existing server/client/common helpers and generic Backup property actions. Connection, queue, authentication, timeouts and teardown belong to the toolkit, not this repository. Use the toolkit environment and explicit ZVE10_TOOLKIT/WIFI_PYTHON settings from docs/install.md. Use the latest companion toolkit main on every host; it includes Windows support and Jiritsu workspace initialization. Update a clean checkout with git switch main and git pull --ff-only origin main before connecting, rerun the offline checks, and keep its source unchanged during a camera session. Preserve local changes if updating fails. Record the actual tested revision as evidence, not an installation requirement. It uses the demonstrated root-shell byte writer. Upload our hash-pinned ARM helpers through the 2.02-tested Jiritsu SET_FILE2 sequence, then GET_FILE and host byte comparison; never restore the unreliable shell hex-chunk upload. Upload mismatch must stop before remount/execution and clean temporary files. Do not launch a one-shot callback probe: keep one persistent service connection throughout sampling. Confirm state.json is `ready` **before asking the owner to use camera menus**. Only one service connection at a time.

For installation, require length **17,694,160**, SHA-256 `5ad8746a229da259fe00b297e8f897d682f7ae9a13393025b3d1c95a808e68d7`, and byte `20` at file offset `0xD778E4` in `/usr/lib/CautionConfig.so`. Expected result: SHA-256 `14f42cc09ee1b9ddde5352482c13b68e5a5e97d9d79e8456087b5e0b7af6ff6a`, exactly one difference `20→1B`. Unknown content must stop. Already patched content should be inspected, not patched again.

Save original full library, `/setting/Backup.bin`, `/setting/Backup.bak`, and the three property values privately on the host before writes. Inspect additionally snapshots before each write; never overwrite earlier evidence. `backup-write` restricts keys/values here and calls the toolkit generic Backup action; the toolkit invokes PMCA-RE readBackup/writeBackup/saveBackup(id >> 16)/readBackup. Do not duplicate that implementation or edit database files directly. For China use `0x01071C54=01`, `0x00A5000B=02`, `0x00A5000C=16` (hex 16 = decimal 22). Do not assume the owner's originals are `00/09/09`.

Never alter BCM4339 firmware, driver, NVRAM, radio calibration, unrelated Backup fields, or other menu libraries. B/C are mode-specific profile selectors, not one selector per band. Do not change sales region or model identity.

## Windows hosts

- **Scope:** Windows on system 2.03 is validated for read-only inspection, Backup-property round trips, and the byte-patch plus `/usr`-remount round trip. WBI writing is unvalidated; 2.02 and the fastboot route have no Windows record. State this scope; never imply a complete Windows install has been tested end to end.
- Prepare with `tools/setup-windows.ps1`; add `-Proxy <url>` when downloads need a proxy because pip ignores `HTTP_PROXY`/`HTTPS_PROXY`. It calls the toolkit's own Windows setup. Install `libusb-win32` with Zadig for both `054C:0D95` and `054C:0336`. The validated session ran in a normal, non-elevated PowerShell; use an elevated one only if opening the device reports access denied.
- Use the toolkit interpreter (`ZVE10_TOOLKIT\linux\.venv\Scripts\python.exe`). Do not pass `--client-uid` and do not use the `.sh` launchers; start `tools/wifi.py serve` directly.
- Windows PowerShell 5 strips plain double quotes in native-program arguments. Keep the backslashes exactly as in `docs/install.md` (`$request = '{\"action\":\"inspect\"}'`).
- Before installation, recommend `raw-backup` with `passes: 2` and `chunk_kib: 4096`, using `--timeout 7200`. Verify every saved-file hash and review both passes' comparisons; `completed: true` alone does not establish identical reads. Windows hardware backup evidence is single-pass. Never call two passes atomic or restore-tested.
- Check the WBI with the read-only `wbi-status` before discussing that step. Only the firmware's `WARMBOOT` dmesg line proves a warm boot; the `PM: Low-level resume` and `Waking up from system sleep` lines also appear on cold boots.
- `wbi-prepare`/`wbi-drop` keep their own guards on every platform: patched library, enabled menu property, unchanged current B/C properties, two matching 60 MiB backups, the confirmation string, and `recovery_ready: true`. Never rewrite an already-invalid WBI and never fabricate those fields.
- End with a power cycle: switch OFF, wait for the access lamp, unplug USB, remove the battery for about 30 seconds.

## Checks, failure, and completion

Follow the concrete commands in docs/install.md. Review each response before the next dependent write. No blind retries on timeout. Stop on mismatched values, short reads, helper failure, unexpected mounts, failed remount, or unknown version. A tool failure after a write does not imply nothing changed; reconnect only after reviewing state and preserved evidence.

Do not power off a camera with a truncated/corrupt library. Never use `cp` over the loaded library or BusyBox `dd` as a writer: the demonstrated versions truncate or run out of space. File offsets are not block-device offsets. Recovery is described separately; do not flash an entire partition just to reverse one byte.

Verify the complete exported library and all three properties after writing, confirm `/usr` read-only, remove the temporary helper, then close normally and wait for `state=closed`, `service_returned=true`, plus `loader_files_removed=true` for Jiritsu or `terminal_closed=true` for the legacy terminal. Ask the owner to switch OFF, wait for the access lamp, unplug USB and remove the battery for about 30 seconds, then reconnect. Create a new persistent ready session, inspect again and check the native menu. Keep that session open during owner interaction and read-only active Wi-Fi sampling.

Battery removal alone may still resume the camera's Warm Boot Image. In the new session inspect boot markers and verify the running Wi-Fi Page1 has five TypeNB items. If it remains TypeRK/four items, stop acceptance and preserve evidence; do not repeat the byte or Backup writes. Use the guarded `wbi-prepare` then `wbi-drop` actions in docs/wbi.md. Preparation must save two matching full 60 MiB backups and return a valid token. Explain the eMMC write and obtain separate explicit owner consent with the returned confirmation string; verify a recovery route before sending `recovery_ready: true`. Never fabricate consent or bypass checks. An already-invalid WBI must not be written again.

Use the read-only `boot-check` action after `inspect`; follow `docs/wbi.md` for the separate Agent-assisted WBI procedure. The WBI action runs only the hash-pinned Sony utility obtained from the owner's official package, with the exact tested configuration and full-partition readback; never bundle Sony's ELF or improvise block writes. Its source package is 2.03; known camera systems 2.02 and 2.03 have distinct pinned libObj fingerprints. Model/system fingerprints, block-node and sysfs geometry checks must pass; missing metadata means stop. This integration needs hardware validation. The 2.03 hardware procedure confirmed only the first 512 WBI bytes changed and the owner confirmed the native band menu after power removal; actual 5 GHz radio functions remain unaccepted. Keep packaged-refactor tests distinct from underlying hardware evidence.

Report file/property state, cold-boot persistence, user-reported menu/function results, and measured active radio state separately. Driver channel lists are not regulatory certification. No performance figures without a benchmark. Restore the exact saved originals on request using docs/recovery.md; don't reset all Backup settings.

## Privacy and handoff

Put all Wi-Fi session output in ignored `private/`. The reused toolkit also maintains its normal session pointer inside its own checkout. They may contain device identity, credentials, and keys; never commit or upload them. Publish only carefully redacted summaries. End with evidence paths, actions completed, current state, recovery readiness, and limitations. Windows 2.03 integration has hardware evidence for inspection, single-pass raw backup, property round trips and the library restore/patch round trip. First-time factory installation and Windows WBI writing remain unvalidated.

For Jiritsu teardown, clean flash helpers while the shell remains alive, close service, then require owner power removal. Never stop the child before remaining USB cleanup. Do not use SIGKILL to cancel backups; use the toolkit cancellation request. No boot-persistent root is installed.


## Prevent known session mistakes

Read the selected toolkit's AGENTS.md and linux/docs/agent-workflow.md before device access. Those instructions cover the same connection reused here. Check host imports/paths/help before the administrator prompt; inventory camera applets before commands. Check available applets before commands. Read proc/sys information using shell cat, not GET_FILE; empty pseudo-file content does not prove root loss.

The original /tmp_network tmpfs is only 1 MiB, and /tmp is flash-backed. Do not enlarge chunks in the shared workspace or spill them into flash. The dedicated 8 MiB/4 MiB research path completed a full single-pass backup at 1.989 MiB/s, and the public raw-backup action now exposes chunk_kib=4096 for this buffer. Follow the documented backup interface and do not invent switches.

Keep one ready session for inspect, changes, readback and menu interaction. A refused diagnostic/missing applet alone is not USB failure. Review response/state before reconnecting; structured-handler exceptions may close the server. Never swallow uncertain write/hash/USB errors to force ready, and never retry patch or WBI blindly. Distinguish USB enumeration from a surviving RAM shell.

Finish all operations and readback before removing owned helpers and unmounting any owned RAM buffer. Then request normal close and wait for actual closed/cleanup flags, not just an accepted response. Jiritsu requires loader_files_removed/service_returned, legacy terminal requires terminal_closed/service_returned. End the remaining Jiritsu child by owner power removal only after service cleanup; do not kill it before GET_FILE verification. Keep error evidence private.

## Community reports and session summaries

Attribute Linux 2.03 / KR2 B=14/C=23 evidence to issue #2. That report used a local change to the former China-only WBI gate. The current WBI code accepts the camera's selected B/C, snapshots them during preparation and checks for changes before execution; it does not choose or write a region.

The reported tools/session_summary.py is absent from this repository and its visible history. Do not invent a replacement or claim it was fixed. Inspect state.json directly: require state=closed and service_returned=true; Jiritsu requires loader_files_removed=true, the legacy terminal requires terminal_closed=true. Do not require terminal_closed on Jiritsu. A successful write-mode session is not a valid_read_only_session merely because cleanup passed.
