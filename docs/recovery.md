# Verification and recovery

**English** | [简体中文](recovery.zh-CN.md)

## Installation acceptance

Separate these observations in the installation record:

1. Complete library hash/length and unique byte difference; three Backup values immediately reread.
2. `/usr` is read-only, temporary helper removed, service closed normally.
3. After USB disconnection and battery removal, a **new** persistent session again reports the patched full hash and menu property `01` with the selected B/C values; run `boot-check` and require TypeNB/five items; record warm-resume markers as boot context. Battery removal alone does not prove a genuine cold boot.
4. Owner can enter the native frequency menu. Menu evidence alone is not proof of 5 GHz radio operation.
5. If requested, test phone photo transfer on the chosen 5 GHz direct hotspot, then separately test router connection and remote shooting. Record actual result and active channel; do not claim a speed improvement without a controlled benchmark.

If the patch and properties match but Page1 remains TypeRK/four items, stop repeated writes and use the [Agent-assisted WBI procedure](wbi.md). Keep the complete `nflasha5` backup private; restore only this camera's own image if the verified recovery plan requires it. Invalidating an obsolete WBI does not permanently disable normal warm boot.

Keep the session ready while asking the owner to use menus. During an active Wi-Fi connection, these fixed read-only radio queries can be requested, for example:

```sh
"$WIFI_PYTHON" -B tools/wifi.py request --session private/verify-01 '{"action":"radio-status","query":"country"}'
"$WIFI_PYTHON" -B tools/wifi.py request --session private/verify-01 '{"action":"radio-status","query":"status"}'
```

Windows PowerShell (the same placeholders and authorization requirements apply):

```powershell
$requestFile = 'private/request.json'
@{ action = 'radio-status'; query = 'country' } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $requestFile -Encoding UTF8
& $wifiPython -B .\tools\wifi.py request --session private/verify-01 --request-file $requestFile
@{ action = 'radio-status'; query = 'status' } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $requestFile -Encoding UTF8
& $wifiPython -B .\tools\wifi.py request --session private/verify-01 --request-file $requestFile
```

`query` also accepts `channels` and `chanspecs`; arbitrary driver commands are refused. Interfaces often disappear when Wi-Fi exits; an idle failure is not a profile measurement. Output may contain identifiers: keep it private. Expected historical China observations are XR/76 in GO and XR/143 in STA, not a promise of any specific selected channel. Driver lists are not compliance tests.

## Normal rollback over USB-C

Confirm the same model, displayed firmware, current known library and the private installation note. Obtain permission for rollback. Start a new persistent `--owner-authorized-write` session and inspect first. The restore helper requires the known complete patched file hash; it refuses unknown or truncated files.

```sh
"$WIFI_PYTHON" -B tools/wifi.py request --session private/restore-01 '{"action":"restore"}'
```

Windows PowerShell (the same placeholders and authorization requirements apply):

```powershell
$requestFile = 'private/request.json'
@{ action = 'restore' } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $requestFile -Encoding UTF8
& $wifiPython -B .\tools\wifi.py request --session private/restore-01 --request-file $requestFile
```

Require the factory SHA-256 `5ad8746a229da259fe00b297e8f897d682f7ae9a13393025b3d1c95a808e68d7`, length 17,694,160, unique difference at `0xD778E4`, and read-only `/usr`.

Restore each Backup property using `backup-write` with its **currently inspected** byte as `expected` and the **owner's saved original** as `value`. For the historical camera only, this was:

```sh
"$WIFI_PYTHON" -B tools/wifi.py request --session private/restore-01 '{"action":"backup-write","id":"0x01071C54","expected":"01","value":"00"}'
"$WIFI_PYTHON" -B tools/wifi.py request --session private/restore-01 '{"action":"backup-write","id":"0x00A5000B","expected":"02","value":"09"}'
"$WIFI_PYTHON" -B tools/wifi.py request --session private/restore-01 '{"action":"backup-write","id":"0x00A5000C","expected":"16","value":"09"}'
```

Windows PowerShell (the same placeholders and authorization requirements apply):

```powershell
$requestFile = 'private/request.json'
@{ action = 'backup-write'; id = '0x01071C54'; expected = '01'; value = '00' } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $requestFile -Encoding UTF8
& $wifiPython -B .\tools\wifi.py request --session private/restore-01 --request-file $requestFile
@{ action = 'backup-write'; id = '0x00A5000B'; expected = '02'; value = '09' } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $requestFile -Encoding UTF8
& $wifiPython -B .\tools\wifi.py request --session private/restore-01 --request-file $requestFile
@{ action = 'backup-write'; id = '0x00A5000C'; expected = '16'; value = '09' } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $requestFile -Encoding UTF8
& $wifiPython -B .\tools\wifi.py request --session private/restore-01 --request-file $requestFile
```

Do not overwrite normal user settings by restoring an entire old Backup database. Do not set unrelated radio power/model fields. If the saved original values are outside this wrapper's limited supported range, stop for review; don't bypass the check. An already-restored property/library can be skipped after verification.

Inspect, close normally, confirm teardown, and cold boot as in installation. Start a new read-only session, inspect factory hash/original properties, and verify original behavior. The reverse-byte helper and property restoration were exercised in Windows 2.03 round trips; factory behavior still requires verification after your own restoration.

## Failed or interrupted installation

Stop after any timeout or mismatch. Inspect state and saved before/after evidence before reconnecting. A command can have changed the camera even if its response was lost. Reestablish only one session, inspect before deciding whether to resume or restore. If USB disappeared after closing service mode, replug; if necessary power-cycle only after confirming system-file integrity.

**Never reboot with a known truncated library.** Do not try `cp` to replace the loaded library: the demonstrated attempt ran out of space and truncated it. Do not use the camera BusyBox `dd` for writes: it lacks working `conv=notrunc` and truncates files. A full-file write is not equivalent to the guarded one-byte writer.

If a write succeeded but remounting read-only failed, preserve the original and after hashes, stop other operations and obtain a qualified recovery review. Do not report the installation as complete. The wrapper stops and does not promise automatic rollback under USB or filesystem failure.

## Camera no longer boots

USB-C service shell requires a normally booting camera. Serious filesystem damage may need additional hardware for BootROM injection and fastboot, using [zv-e10-toolkit recovery](https://github.com/dino2048/zv-e10-toolkit). Review its current docs and hardware requirements before attempting it. No hardware recovery payload or personal partition image is bundled here.

Use the same camera's verified original backup, correct partition table and exact lengths, then read back and compare the whole restored partition. Never flash another camera's Backup, calibration or keys. Never treat `0xD778E4` as a partition offset. Restoring whole old partitions can reintroduce prior experiments and overwrite later changes. Backups and fastboot do not guarantee recovery in every failure mode.

## WBI failure evidence

See [WBI recovery](wbi.md) for exact commands. Preserve both full backups, prewrite/after reads and JSON diagnostics. Never automatically reflash old WBI. A consumed token or timeout requires review, not a retry; only this camera's own verified image may be used through the established fastboot recovery route, followed by complete readback. This release has no hardware-tested WBI restoration.


An updated warm image can also restore the unlocked five-item menu. Warm-resume logs alone do not justify repeating WBI invalidation when menu, file and properties are correct.
