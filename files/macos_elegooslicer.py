"""Install the configured DMG bundle without merging or touching user profiles."""

import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True)


def metadata(app):
    if app.is_symlink() or not app.is_dir():
        raise ValueError("Not a regular application bundle: {}".format(app))
    with (app / "Contents/Info.plist").open("rb") as stream:
        info = plistlib.load(stream)
    keys = ("CFBundleIdentifier", "CFBundleShortVersionString")
    values = tuple(info.get(key) for key in keys)
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise ValueError("Missing bundle identity/version metadata: {}".format(app))
    build = info.get("CFBundleVersion", "")
    if not isinstance(build, str):
        raise ValueError("Invalid bundle build metadata: {}".format(app))
    # Upstream can omit or leave the build blank; None means unavailable, not a build.
    values += (build if build.strip() else None,)
    executable = info.get("CFBundleExecutable")
    if not isinstance(executable, str) or not executable or Path(executable).name != executable:
        raise ValueError("Invalid bundle executable: {}".format(app))
    binary = app / "Contents/MacOS" / executable
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise ValueError("Missing executable bundle binary: {}".format(binary))
    return values


def replace(source, target):
    desired = metadata(source)  # Validate before touching the existing bundle.
    if target.is_symlink():
        raise ValueError("Refusing to replace a symlink: {}".format(target))
    if target.exists():
        try:
            installed = metadata(target)
        except (OSError, ValueError, plistlib.InvalidFileException):
            installed = None
        if installed == desired:
            return False
        if installed and installed[0] != desired[0]:
            raise ValueError("Installed and downloaded bundle identifiers differ")

    # Same filesystem as target: rename swaps whole bundles, never merges stale files.
    workspace = Path(tempfile.mkdtemp(prefix=".elegooslicer-", dir=str(target.parent)))
    staged, backup = workspace / "ElegooSlicer.app", workspace / "previous.app"
    try:
        run("/usr/bin/ditto", str(source), str(staged))
        if metadata(staged) != desired:
            raise ValueError("Staged bundle metadata differs from downloaded bundle")
        if target.exists():
            target.rename(backup)
        try:
            staged.rename(target)
        except Exception:
            if backup.exists():
                try:
                    backup.rename(target)
                except Exception as rollback_error:
                    print("Rollback failed; prior bundle retained at {}: {}".format(
                        backup, rollback_error), file=sys.stderr)
            raise  # Preserve the original replacement error.
        if backup.exists():
            shutil.rmtree(backup)
        return True
    finally:
        if backup.exists():
            print("Prior bundle retained at {}".format(backup), file=sys.stderr)
        else:
            try:
                shutil.rmtree(workspace)
            except OSError as cleanup_error:
                print("Staging cleanup failed: {}".format(cleanup_error), file=sys.stderr)


def install(dmg, target=Path("/Applications/ElegooSlicer.app")):
    workspace = Path(tempfile.mkdtemp(suffix=".elegooslicer-mount"))
    volume = workspace / "volume"
    volume.mkdir()
    try:
        # Explicit mountpoint supports spaces and permits cleanup after partial attach.
        run("/usr/bin/hdiutil", "attach", str(dmg), "-nobrowse", "-readonly",
            "-mountpoint", str(volume))
        return replace(volume / "ElegooSlicer.app", target)
    finally:
        try:
            run("/usr/bin/hdiutil", "detach", str(volume))
        except Exception as detach_error:
            # Do not delete a possibly mounted filesystem or mask the primary error.
            print("Detach failed; mount directory retained at {}: {}".format(
                workspace, detach_error), file=sys.stderr)
        else:
            try:
                shutil.rmtree(workspace)
            except OSError as cleanup_error:
                print("Mount cleanup failed: {}".format(cleanup_error), file=sys.stderr)


if __name__ == "__main__":
    try:
        changed = install(Path(sys.argv[1]))
        print("ELEGOOSLICER_CHANGED" if changed else "ELEGOOSLICER_CURRENT")
    except Exception as error:
        print("ElegooSlicer installation failed: {}".format(error), file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError):
            print(error.stderr, file=sys.stderr)
        sys.exit(1)
