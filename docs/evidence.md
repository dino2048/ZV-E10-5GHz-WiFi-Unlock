# Firmware differences and validation results

**English** | [简体中文](evidence.zh-CN.md)

Native frequency-band menu unlocking has been verified on first-generation Sony ZV-E10 cameras running **2.02 and 2.03**. Both use the same Wi-Fi changes and WBI procedure; connection and backup transport are the main differences.

## Version comparison

| Item | 2.02 | 2.03 |
| --- | --- | --- |
| System identifier | `30110_05.2025031501` | `30110_06.2026060501` |
| Root session | Original terminal backend | Jiritsu; start with `--backend jiritsu --firmware 2.03 --owner-authorized-exec` |
| Backup transport | Direct continuous FileControl reads | Root reads to a RAM file, downloaded through Jiritsu |
| Complete backup evidence | User+B0/B1 double reads; also fastboot double backups | Complete user+B0/B1 single pass, with chunk and full saved-file host checks |
| Backup rate | About 12 MiB/s via Linux FileControl | About 1.3 MiB/s with 512 KiB staging; 1.989 MiB/s for the complete dedicated-buffer pass |
| Wi-Fi changes | One file byte and three Backup properties | Same changes |
| WBI handling | Two full backups, Sony utility, complete after comparison | Same procedure; version-specific system fingerprint |
| Native band menu | TypeNB/five items, working 2.4/5 GHz menu | TypeNB/five items, working 2.4/5 GHz menu |

A persistent Jiritsu session retains one shell's state; it does not install boot-persistent root. The old terminal path failed and FileControl returned 0x80/no data on the tested 2.03 device, so Jiritsu was used. This does not establish universal protocol removal. The versions have different libObj.so fingerprints, checked separately before WBI operations.

## Shared configuration and modification checks

Tests used macOS, USB-C and the mainland China configuration B=2/C=22: hotspot XR/76 and router XR/143.

- CautionConfig.so: 17,694,160 bytes; the target factory library is identical across these versions.
- Factory SHA-256: `5ad8746a229da259fe00b297e8f897d682f7ae9a13393025b3d1c95a808e68d7`.
- Patched SHA-256: `14f42cc09ee1b9ddde5352482c13b68e5a5e97d9d79e8456087b5e0b7af6ff6a`.
- Exactly one byte differs: offset `0xD778E4`, `20 → 1B`, written in place without truncation.
- Backup values saved and reread: `0x01071C54=01`, `0x00A5000B=02`, `0x00A5000C=16` (hex 16 = decimal 22).
- Changes persisted after restart; /usr returned read-only and uploaded helpers were removed.

Warm resume can retain the old TypeRK/four-item page. On both versions, the [WBI procedure](wbi.md) saved two matching complete 60 MiB originals and rechecked before execution. The same Sony tool returned `[UD_WBI_DROP] /dev/nflasha5 wbi_drop`. Complete after-read comparison showed only the first 512 bytes zeroed, with every remaining byte unchanged; the native menu was available after restart.

## Wireless function records

On 2.02, 5 GHz phone photo transfer and remote capture/photo reception through a 5 GHz router succeeded. The active driver reported hotspot XR/76 and router XR/143, including hotspot channel 157/80 MHz and router channel 40/80 MHz. The 2.03 records cover file/property persistence, WBI handling and the running TypeNB/five-item menu. Results belong to the firmware actually tested.

## Complete 2.03 backup

A dedicated 8 MiB tmpfs and 4 MiB chunks read:

| Region | Bytes |
| --- | ---: |
| Linux-visible user area, including gaps/tail | 1,954,545,664 |
| B0 boot area | 4,194,304 |
| B1 boot area | 4,194,304 |
| Total | 1,962,934,272 |

Camera/host hashes matched for every chunk, followed by full saved-file host rereads. The action took **940.956 seconds, averaging 1.989 MiB/s**, including preflight, metadata, saved-file verification and RAM mount cleanup; USB setup/admin waiting are excluded. No disconnect occurred during the read.

A research wrapper managed the larger buffer; the public toolkit CLI still defaults to 512 KiB. Do not invent a public 4 MiB switch. A live single pass, independent double pass, atomic snapshot and restore validation are distinct. Scope excludes RPMB, OTP/eFuse and hidden areas.

Short-read cancellation also retained an incomplete file/manifest with matching host reread, and the connection remained usable. The dedicated mount and mountpoint were removed, loader cleanup was verified and service returned normally. Owner power removal ends the remaining RAM shell.

## Published tools and reproducible checks

The installer reuses toolkit sessions, transport and generic Backup actions. Version/hash guards, upload readback and WBI transaction guards have offline tests; hardware evidence covers the operations above. See [offline-checks.json](offline-checks.json) and [AGENTS.md](../AGENTS.md).

Use in-place byte writes, never whole-file cp or truncating dd replacement. Installation saves each owner's original files/properties/WBI privately; do not substitute another camera's data. See [technical notes](technical.md) and [recovery](recovery.md).

The Sony WBI utility is extracted offline from the owner's official 2.03 package. That package version does not require the installed camera to be 2.03: both known systems use the same exact tool hash. No Sony firmware/tool, camera image, key or private session is distributed.

## Sources

- [Sony A7C Frequency Band](https://helpguide.sony.net/ilc/2020/v1/en/contents/TP1000156044.html): native menu and direct-connection scope.
- [Sony A7C Access Point Set.](https://helpguide.sony.net/ilc/2020/v1/en/contents/TP1000115299.html): router setup.
- [Sony ZV-E10 PC Remote](https://helpguide.sony.net/ilc/2070/v1/en/contents/TP0002392805.html): direct/AP methods, pairing, capture and storage.
- [Sony A7C specifications](https://helpguide.sony.net/ilc/2020/v1/en/contents/TP1000156734.html): regional wireless variants.
- [IFT Sony equipment inventory](https://www.ift.org.mx/node/19562): ZV-E10 Type1DR entry.
- [NTC 2021 inventory](https://region7.ntc.gov.ph/wp-content/uploads/2024/01/RCE_08312021.pdf): A7C Type1DR entry, printed page 187.
- [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE), [MIT license](https://github.com/ma1co/Sony-PMCA-RE/blob/master/LICENSE.txt): service protocol; the toolkit pins `a82f5baaa8e9c3d9f28f94699e860fb2e48cc8e0`.
- [zv-e10-toolkit](https://github.com/dino2048/zv-e10-toolkit): backup, persistent service and recovery. This project uses commit `2255eef9a5ec7b459f19c444c29166f547949a67`.
