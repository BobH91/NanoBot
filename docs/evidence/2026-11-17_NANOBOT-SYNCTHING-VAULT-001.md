# NANOBOT-SYNCTHING-VAULT-001 — Three-Node Obsidian Vault Synchronization

## Status

PASS — THREE-NODE SYNCHRONIZATION VERIFIED

Verification date: 2026-11-17

## Purpose

Record the verified Syncthing synchronization baseline for the NanoBot
Obsidian documentation vault across Lenovo, Raspberry Pi 5, and Orin Nano.

This record documents synchronization state. It does not change or redefine
the NanoBot software architecture, execution paths, or hardware configuration.

## Canonical Vault Paths

| Node | Host | Vault path |
|---|---|---|
| Lenovo | bob-IdeaPad-3-15IGL05 | `/home/bob/NanoBot/vault` |
| Raspberry Pi 5 | raspberrypi | `/home/pi/NanoBot/vault` |
| Orin Nano | Nanobot | `/home/bob/NanoBot/vault` |

The `.stfolder` marker was present at each verified vault path.

## Synchronization Verification

All three nodes reported the Syncthing folder in the `idle` state after
synchronization.

The database status reported the following values on each node:

| Metric | Lenovo | Raspberry Pi 5 | Orin Nano |
|---|---:|---:|---:|
| Local files | 47 | 47 | 47 |
| Local directories | 8 | 8 | 8 |
| Local indexed bytes | 8,025,691 | 8,025,691 | 8,025,691 |
| Global files | 47 | 47 | 47 |
| Needed files | 0 | 0 | 0 |
| Needed directories | 0 | 0 | 0 |
| Needed deletes | 0 | 0 | 0 |
| In-sync files | 47 | 47 | 47 |
| In-sync indexed bytes | 8,025,691 | 8,025,691 | 8,025,691 |
| Errors | 0 | 0 | 0 |
| Pull errors | 0 | 0 | 0 |

Both remote peers were reported connected from each node's perspective.

The self-device entry is not a remote connection and is excluded from
that peer-connectivity statement.

## Filesystem Manifest

The independently generated pre-synchronization filesystem manifests
matched across all three nodes:

- Files: 47
- Directories: 8
- Total file bytes: 8,024,667
- SHA-256: `504bac8fa2ec237e293a3c4c5d7b43a6911e4ce388e1ba96e7478e82b85e58f9`

The manifest byte count (8,024,667) and Syncthing database indexed byte
count (8,025,691) are different measurements. They are recorded separately
and are not treated as interchangeable.

## Vault Backups

Verified vault archive backups from 2026-11-16:

| Node | Archive | SHA-256 |
|---|---|---|
| Lenovo | `/home/bob/NanoBot-vault-backup-20261116-lenovo.tar.gz` | `79ae1949cbb4a22029a6c27b49d9e5e4f0af9dbb7dd9249c1c94220e6924455e` |
| Raspberry Pi 5 | `/home/pi/NanoBot-vault-backup-20261116-pi.tar.gz` | `248a54326d2d13427d7c73726072711f4fa61dc957cf63ade36ef14700809ae4` |
| Orin Nano | `/home/bob/NanoBot-vault-backup-20261116-orin.tar.gz` | `b45d06bf7e5358ff39667bffc1817ffe9c708630ad903bbf18d68529c09ebb89` |

## Syncthing Configuration Backups

Verified configuration backup files from 2026-11-16:

| Node | Configuration backup | SHA-256 |
|---|---|---|
| Lenovo | `/home/bob/syncthing-config-backup-20261116/config.xml` | `80b1ce02efd11090672331dfe7c525ed975254dbb75df6039bf6e1f05cd1ae4d` |
| Raspberry Pi 5 | `/home/pi/syncthing-config-backup-20261116/config.xml` | `b6f585ee83d19d8d29327bb0327321c7cb9d7df54e3bd46cd6460ee1c8cc6e28` |
| Orin Nano | `/home/bob/syncthing-config-backup-20261116/config.xml` | `921a5a9c76b821b9cdf8a0a47dcc5f77a8b5ce19a8ca191f802c623842b75e54` |

## Change Control

- No NanoBot execution code was changed as part of this verification.
- No motor, servo, camera, or calibration setpoints were changed.
- No service restart or Syncthing database reset was performed as part of
  the synchronization verification.
- Vault and Syncthing configuration backups were retained.
- The vault remains documentation; this record does not authorize placing
  execution code in the vault.

## Conclusion

The three NanoBot nodes reported matching Syncthing database status,
zero outstanding synchronization needs, zero errors, and connected
remote peers.

The pre-synchronization filesystem manifests also matched by file count,
directory count, total file bytes, and SHA-256.

This establishes the recorded three-node synchronization baseline
for 2026-11-17. It does not establish that future synchronization
will remain healthy without subsequent verification.
