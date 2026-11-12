# ZV-E10 2.03 evidence and limitations

**Latest complete single-pass hardware result (2026-11-12):** A dedicated 8 MiB tmpfs and 4 MiB chunks read the entire user area plus B0/B1: 1,962,934,272 bytes. Camera/host chunk hashes and complete saved-file host rereads matched. The backup action took 940.956 seconds, averaging 1.989 MiB/s, including preflight, metadata, saved-file verification and RAM mount cleanup; USB-session setup/admin waiting are excluded. No disconnect occurred during the read; mount/helper cleanup and service close succeeded. This is one live-system pass, not double-pass or restore validation. A research wrapper managed the larger buffer; the public CLI still defaults to 512 KiB. Earlier partial-read/1.3 MiB/s observations below are historical.


**English** | [简体中文](firmware-203.zh-CN.md)

These are the 2026-11-12 observations on one first-generation ZV-E10 upgraded officially from 2.02 to **2.03**, `/version.txt` = `30110_06.2026060501`. The packaged host refactor has offline tests; this record describes its underlying camera procedure.

## Root shell and backup

The old terminal path failed and FileControl returned `0x80` with no data on this device. The Jiritsu loader executed a persistent root shell: PID, variables and working directory survived subsequent commands. This is a temporary session, not root installed across reboots. The name alone does not establish that Jiritsu is an officially documented repair interface.

Root `dd` read 512 KiB chunks into tmpfs, transferred by Jiritsu, with camera/host SHA-256 comparison. Speed was about **1.3 MiB/s**, around 25 minutes per user-area pass. The owner stopped the experiment at **1,681,915,904 bytes**. That preliminary run did not complete all regions; the subsequent complete single pass is reported above. Independent double-pass validation remains pending. A complete double fastboot backup had been verified on this same camera **before upgrading**, while it ran 2.02. See toolkit's Jiritsu documentation for the slow backup action and cancellation.

Removing flash loader/script/output while the RAM shell remained alive, then closing service and removing power, succeeded. Stopping the shell first repeatedly caused subsequent USB reads to time out; the internal cause is unproven. The packaged cancellation and cleanup code have offline validation only.

## Wi-Fi changes and WBI

The complete 17,694,160-byte `CautionConfig.so` matched the known 2.02 original:

- Original SHA-256: `5ad8746a229da259fe00b297e8f897d682f7ae9a13393025b3d1c95a808e68d7`.
- Patched SHA-256: `14f42cc09ee1b9ddde5352482c13b68e5a5e97d9d79e8456087b5e0b7af6ff6a`.
- Exactly one byte differed: offset `0xD778E4`, `20 → 1B`.
- Backup values: `0x01071C54=01`, `0x00A5000B=02`, `0x00A5000C=16` (China, owner-confirmed B=2/C=22).

The file/properties persisted, but warm resume retained the four-item page. The guarded WBI procedure saved two matching complete 60 MiB originals and another matching prewrite read:

- Before SHA-256: `aa584ec93b17f786e6ffbdfe732ce351a17d3219119f0c549741999eea4832e5`.
- Sony output: `[UD_WBI_DROP] /dev/nflasha5 wbi_drop`.
- After SHA-256: `2e78fd8a55186d1b28c688a96fee2a812d357bc40520408fc8cffea9389787e2`.
- Complete comparison: only the first 512 bytes were zeroed; all remaining bytes matched.

`/usr` was restored read-only and uploaded helpers were removed. After power removal the owner **confirmed the native frequency-band menu appeared**. Postboot TypeNB/active radio capture and actual 5 GHz hotspot/router tests remain pending on 2.03. The 2.02 functional results must not be presented as 2.03 results. WBI invalidation is an additional disk change beyond the one byte and three properties; normal logs/cache may also change.

## Official tool extraction

The offline extractor was rerun against the owner's 376,353,248-byte `Update_ZVE10V203.exe`, SHA-256 `386970919b758b59de849cd954efd31de00e5f9e435056ce99a7c212a4aca584`. It decoded the embedded CAB and used the pinned fwtool parser, reproducing the exact 6,200-byte Sony utility hash in [WBI instructions](wbi.md). No Sony firmware, utility, camera backup or private session is distributed.
