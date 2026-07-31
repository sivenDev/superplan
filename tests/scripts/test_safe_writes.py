from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "skills" / "using-superplan" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from safe_writes import TextUpdate, commit_text_updates, workspace_lock


class SafeWritesTests(unittest.TestCase):
    def test_commit_rejects_changed_preflight_source_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            first = root / "first.md"
            second = root / "second.md"
            first.write_text("external\n", encoding="utf-8")
            second.write_text("second original\n", encoding="utf-8")

            with self.assertRaisesRegex(OSError, "changed since preflight"):
                commit_text_updates(
                    [
                        TextUpdate(first, "first original\n", "first updated\n"),
                        TextUpdate(second, "second original\n", "second updated\n"),
                    ]
                )

            self.assertEqual(first.read_text(encoding="utf-8"), "external\n")
            self.assertEqual(second.read_text(encoding="utf-8"), "second original\n")

    def test_commit_rolls_back_earlier_replacement_after_later_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            first = root / "first.md"
            second = root / "second.md"
            first.write_text("first original\n", encoding="utf-8")
            second.write_text("second original\n", encoding="utf-8")
            real_replace = os.replace
            failed = False

            def flaky_replace(source: str | bytes, destination: str | bytes) -> None:
                nonlocal failed
                if Path(destination) == second and not failed:
                    failed = True
                    raise OSError("simulated second replace failure")
                real_replace(source, destination)

            with mock.patch("safe_writes.os.replace", side_effect=flaky_replace):
                with self.assertRaisesRegex(OSError, "simulated second replace failure"):
                    commit_text_updates(
                        [
                            TextUpdate(first, "first original\n", "first updated\n"),
                            TextUpdate(second, "second original\n", "second updated\n"),
                        ]
                    )

            self.assertEqual(first.read_text(encoding="utf-8"), "first original\n")
            self.assertEqual(second.read_text(encoding="utf-8"), "second original\n")
            self.assertEqual(sorted(path.name for path in root.iterdir()), ["first.md", "second.md"])

    def test_commit_rechecks_sources_after_staging(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            target = root / "target.md"
            target.write_text("original\n", encoding="utf-8")
            from safe_writes import _stage_text

            stage_count = 0

            def change_during_staging(path: Path, content: str, mode: int) -> Path:
                nonlocal stage_count
                staged = _stage_text(path, content, mode)
                stage_count += 1
                if stage_count == 2:
                    target.write_text("external\n", encoding="utf-8")
                return staged

            with mock.patch("safe_writes._stage_text", side_effect=change_during_staging):
                with self.assertRaisesRegex(OSError, "changed since preflight"):
                    commit_text_updates(
                        [TextUpdate(target, "original\n", "updated\n")]
                    )

            self.assertEqual(target.read_text(encoding="utf-8"), "external\n")
            self.assertEqual(sorted(path.name for path in root.iterdir()), ["target.md"])

    def test_commit_preserves_existing_mode_and_creates_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            existing = root / "existing.md"
            created = root / "nested" / "created.md"
            existing.write_text("old\n", encoding="utf-8")
            existing.chmod(0o640)

            changed = commit_text_updates(
                [
                    TextUpdate(existing, "old\n", "new\n"),
                    TextUpdate(created, None, "created\n"),
                ]
            )

            self.assertEqual(changed, [existing, created])
            self.assertEqual(existing.read_text(encoding="utf-8"), "new\n")
            self.assertEqual(existing.stat().st_mode & 0o777, 0o640)
            self.assertEqual(created.read_text(encoding="utf-8"), "created\n")

    def test_commit_reports_rollback_failure_with_the_affected_path(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            first = root / "first.md"
            second = root / "second.md"
            first.write_text("first original\n", encoding="utf-8")
            second.write_text("second original\n", encoding="utf-8")
            real_replace = os.replace
            call_count = 0

            def fail_write_and_rollback(source: str | bytes, destination: str | bytes) -> None:
                nonlocal call_count
                call_count += 1
                if call_count == 2:
                    raise OSError("simulated second replace failure")
                if call_count == 3:
                    raise OSError("simulated rollback failure")
                real_replace(source, destination)

            with mock.patch("safe_writes.os.replace", side_effect=fail_write_and_rollback):
                with self.assertRaisesRegex(
                    OSError,
                    r"rollback failed: .*first\.md: simulated rollback failure",
                ):
                    commit_text_updates(
                        [
                            TextUpdate(first, "first original\n", "first updated\n"),
                            TextUpdate(second, "second original\n", "second updated\n"),
                        ]
                    )

            self.assertEqual(first.read_text(encoding="utf-8"), "first updated\n")
            self.assertEqual(second.read_text(encoding="utf-8"), "second original\n")

    def test_workspace_lock_serializes_competing_processes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            script = (
                "import sys\n"
                f"sys.path.insert(0, {str(SCRIPTS_DIR)!r})\n"
                "from pathlib import Path\n"
                "from safe_writes import workspace_lock\n"
                f"with workspace_lock(Path({str(root)!r})):\n"
                "    print('acquired', flush=True)\n"
            )

            with workspace_lock(root):
                process = subprocess.Popen(
                    [sys.executable, "-c", script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                time.sleep(0.2)
                self.assertIsNone(process.poll())

            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, msg=stderr)
            self.assertEqual(stdout, "acquired\n")
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
