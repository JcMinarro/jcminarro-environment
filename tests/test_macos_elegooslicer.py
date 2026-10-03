"""Local bundle fixtures; all macOS subprocess calls are replaced, never executed."""

import contextlib
import importlib.util
import io
from pathlib import Path
import plistlib
import shutil
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "installer", Path(__file__).resolve().parents[1] / "files/macos_elegooslicer.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


def bundle(path, version="internal-5", build="42"):
    (path / "Contents/MacOS").mkdir(parents=True)
    with (path / "Contents/Info.plist").open("wb") as stream:
        plistlib.dump({"CFBundleIdentifier": "test.slicer",
                      "CFBundleShortVersionString": version,
                      "CFBundleVersion": build,
                      "CFBundleExecutable": "slicer"}, stream)
    binary = path / "Contents/MacOS/slicer"
    binary.write_text("fixture")
    binary.chmod(0o755)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.source, self.target = root / "download.app", root / "installed.app"
        bundle(self.source)
        self.run = patch.object(installer, "run", side_effect=self.copy).start()
        self.addCleanup(patch.stopall)

    def copy(self, *args):
        self.assertEqual(args[0], "/usr/bin/ditto")
        shutil.copytree(args[1], args[2])

    def test_missing_installs_and_current_does_not_copy(self):
        self.assertTrue(installer.replace(self.source, self.target))
        self.run.reset_mock()
        self.assertFalse(installer.replace(self.source, self.target))
        self.run.assert_not_called()

    def test_outdated_replaces_without_stale_files(self):
        bundle(self.target, "old")
        (self.target / "stale").touch()
        self.assertTrue(installer.replace(self.source, self.target))
        self.assertFalse((self.target / "stale").exists())
        self.assertEqual(installer.metadata(self.source), installer.metadata(self.target))

    def test_build_difference_updates(self):
        bundle(self.target, build="41")
        self.assertTrue(installer.replace(self.source, self.target))

    def test_invalid_download_preserves_installed(self):
        bundle(self.target, "old")
        (self.source / "Contents/MacOS/slicer").unlink()
        with self.assertRaises(ValueError):
            installer.replace(self.source, self.target)
        self.assertEqual(installer.metadata(self.target)[1], "old")
        self.run.assert_not_called()

    def test_copy_failure_preserves_installed_and_cleans_stage(self):
        bundle(self.target, "old")
        self.run.side_effect = OSError("copy failed")
        with self.assertRaisesRegex(OSError, "copy failed"):
            installer.replace(self.source, self.target)
        self.assertEqual(installer.metadata(self.target)[1], "old")
        self.assertFalse(list(self.target.parent.glob(".elegooslicer-*")))

    def test_invalid_stage_preserves_installed(self):
        bundle(self.target, "old")

        def corrupt_copy(*args):
            self.copy(*args)
            (Path(args[2]) / "Contents/Info.plist").unlink()

        self.run.side_effect = corrupt_copy
        with self.assertRaises(FileNotFoundError):
            installer.replace(self.source, self.target)
        self.assertEqual(installer.metadata(self.target)[1], "old")

    def test_replacement_failure_restores_prior_bundle(self):
        bundle(self.target, "old")
        rename = Path.rename

        def fail_stage(path, destination):
            if path.name == "ElegooSlicer.app":
                raise OSError("replacement failed")
            return rename(path, destination)

        with patch.object(Path, "rename", fail_stage):
            with self.assertRaisesRegex(OSError, "replacement failed"):
                installer.replace(self.source, self.target)
        self.assertEqual(installer.metadata(self.target)[1], "old")

    def test_rollback_failure_retains_backup_and_original_error(self):
        bundle(self.target, "old")
        rename = Path.rename

        def fail_swap(path, destination):
            if path.name in ("ElegooSlicer.app", "previous.app"):
                raise OSError("failed " + path.name)
            return rename(path, destination)

        with patch.object(Path, "rename", fail_swap), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaisesRegex(OSError, "failed ElegooSlicer.app"):
                installer.replace(self.source, self.target)
        backup = next(self.target.parent.glob(".elegooslicer-*/previous.app"))
        self.assertEqual(installer.metadata(backup)[1], "old")

    def test_partial_mount_failure_detaches_and_preserves_error(self):
        mount_root = self.target.parent / "mount"
        mount_root.mkdir()
        self.run.side_effect = [OSError("attach failed"), None]
        with patch.object(installer.tempfile, "mkdtemp", return_value=str(mount_root)):
            with self.assertRaisesRegex(OSError, "attach failed"):
                installer.install("fixture.dmg", self.target)
        self.assertEqual(self.run.call_args.args[1], "detach")
        self.assertFalse(mount_root.exists())

    def test_mount_install_and_detach_with_bundle_fixture(self):
        def macos_fixture(*args):
            if args[1] == "attach":
                shutil.copytree(self.source, Path(args[-1]) / "ElegooSlicer.app")
            elif args[1] != "detach":
                self.copy(*args)

        self.run.side_effect = macos_fixture
        self.assertTrue(installer.install("fixture.dmg", self.target))
        self.assertFalse(installer.install("fixture.dmg", self.target))
        self.assertEqual(self.run.call_args.args[1], "detach")
        self.assertFalse(Path(self.run.call_args.args[2]).parent.exists())

    def test_detach_failure_preserves_original_error_and_mount_directory(self):
        mount_root = self.target.parent / "mount"
        mount_root.mkdir()
        self.run.side_effect = [OSError("attach failed"), OSError("detach failed")]
        with patch.object(installer.tempfile, "mkdtemp", return_value=str(mount_root)):
            with contextlib.redirect_stderr(io.StringIO()) as warnings:
                with self.assertRaisesRegex(OSError, "attach failed"):
                    installer.install("fixture.dmg", self.target)
        self.assertIn("Detach failed", warnings.getvalue())
        self.assertTrue(mount_root.exists())


if __name__ == "__main__":
    unittest.main()
