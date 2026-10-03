# macOS ElegooSlicer updates

## Objective and scope
Allow an existing macOS ElegooSlicer installation to reach the release configured by the role without removing user profiles or changing Slack/cask handling or Linux behavior.

## Problem and approach
The current installer checks bundle existence only, preventing updates. Inspect version metadata and safely replace outdated bundles, validating the downloaded application before replacing the existing installation. Preserve cleanup and a recovery path. Do not assume release filenames equal bundle metadata without evidence.

## Execution
- Authorized scope: macOS ElegooSlicer installer, focused checks and relevant documentation.
- Route: delegated direct; preparation and multi-file writer triggers.
- TDD: off for this change by explicit user authorization to implement with local checks and subsequent manual macOS execution.
- Runner/checks: `ansible-playbook --syntax-check provision.yml`; focused installer syntax harness and behavior checks selected from available tooling by the writer.
- No local provisioning or remote machine access. Actual macOS installation is pending user verification.
- Delivery: ask-on-risk; forecast 200–300, actual 392 authored changed lines in one cohesive work unit (352 additions, 40 deletions). No push or PR authorized.
- RDD: on (global). Initial review boundary: `f4d00a8`.
- Preserve existing untracked `.atl/` and `.codegraph/`.

## Work units
- [x] T1: Implement safe idempotent macOS installation/update with focused regression checks and usage documentation. Local bundle fixtures verify missing/current/outdated applications, check mode and failure preservation. Real macOS verification remains pending.

## Acceptance
- Existing outdated applications can update; already-current applications are not replaced.
- Invalid downloads do not destroy the installed app; cleanup and recovery are retained.
- User configuration is untouched and casks can still be skipped.
- Required checks and macOS limitations are reported honestly.

## Evidence and next step
Implementation candidate on `fix/macos-elegooslicer-update`, based on `f4d00a8`; work-unit commit pending (parent records the resulting hash). No push, PR or native review performed. Engram save was attempted and rejected because multiple active runtime sessions match this project/directory; full mirror remains pending and no session identity was invented.

### Behavior and limitations
- Every normal run downloads the configured DMG and mounts it to compare actual `CFBundleIdentifier`, `CFBundleShortVersionString` and `CFBundleVersion`. No release-to-metadata equivalence is assumed. This adds download/mount overhead even when current; transient work is not reported as a bundle change.
- Downloaded and staged bundles must have nonempty identity/version metadata and an executable binary. Matching installed metadata leaves the bundle untouched; different versions converge to the configured artifact, including intentional downgrades. Different valid identifiers and installed symlinks are rejected. This is structural validation, not signature or checksum authentication.
- `ditto` copies into a new sibling staging directory; whole-bundle renames prevent stale-file merging. Replacement failure restores the prior bundle. If rollback fails, the prior bundle is retained at the reported backup path. Detach/cleanup errors are reported without hiding the primary installer error; failed detach retains the mount directory for manual recovery.
- User profiles are untouched. Quit ElegooSlicer before provisioning. The target user needs write access to `/Applications`; no privilege escalation is added. Real macOS tools and release metadata have not been exercised locally.
- Check mode explicitly reports comparison unavailable and skips download, mount and replacement; it does not predict whether the configured release would change the app.

### Local verification
Commands below are run with RTK pass-through for Ansible commands; results include the ordinary implicit-localhost/no-inventory warnings.

| Command | Observed result |
|---|---|
| `rtk ansible-playbook --syntax-check provision.yml` | Passed, run once in foreground. |
| `rtk ansible-playbook --syntax-check tests/macos_elegooslicer_syntax.yml` | Passed; static import parses the installer on Linux. |
| `rtk ansible-playbook --check tests/macos_elegooslicer_syntax.yml` | Passed: ok=1, changed=0, failed=0, skipped=4; no download or macOS subprocess. |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_macos_elegooslicer.py' -v` | Passed: 11 tests, 0.023s, OK (initial 10-test suite also passed). |
| `rtk git diff --check` | Passed with no output; staged diff also checked before commit. |

Runtime boundary: local fixtures execute the real Python installer flow with macOS subprocesses replaced; they do not validate `hdiutil`, `ditto`, permissions or vendor bundle layout on macOS. Rollback boundary: revert this work unit's installer YAML, Python helper, focused tests and this task document only; Linux/defaults/casks remain unchanged.

### User macOS verification (pending)
From the role directory, after quitting the app:

```bash
ansible-playbook -K provision.yml --skip-tags casks
```

This is full provisioning without casks, NOT an isolated ElegooSlicer run. The requirements play remains `always` and can install dependencies. Verify the first update and subsequent unchanged bundle, then launch ElegooSlicer and confirm profiles remain available. Native review is delegated to the parent after the work-unit commit.
