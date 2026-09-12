"""Checks for evaluator false failures, not tests of the LFG product."""
import unittest
import tempfile
from pathlib import Path
from collect import estimate, read_inventory
from evaluate import seed

class Measurements(unittest.TestCase):
    def read(self, command):
        return read_inventory([{'name':'exec_command','input':{'cmd':command,'workdir':'/fixture'}}], '/elsewhere')

    def test_output_target_and_echo_are_not_reads(self):
        reads, _ = self.read('echo label.md; cat input.md > output.md')
        self.assertEqual([r['path'] for r in reads], ['/fixture/input.md'])

    def test_repeated_source_reads_count_twice(self):
        reads, _ = self.read("sed -n '1,80p' notes.md && nl -ba notes.md | head -20")
        self.assertEqual([r['path'] for r in reads], ['/fixture/notes.md'] * 2)

    def test_quoted_custom_path_and_workdir(self):
        reads, _ = self.read('cd ..; cat "knowledge space/STATE.md"')
        self.assertEqual([r['path'] for r in reads], ['/knowledge space/STATE.md'])

    def test_shell_variable_and_glob_remain_unknown(self):
        reads, opaque = self.read('cat "$source" logs/adr/*.md')
        self.assertEqual(reads, [])
        self.assertEqual(opaque, [0])

    def test_direct_read_is_counted(self):
        reads, _ = read_inventory([{'name':'Read','input':{'file_path':'/fixture/notes.md'}}], '/fixture')
        self.assertEqual(len(reads), 1)

    def test_round_each_output_separately(self):
        self.assertEqual(sum(map(estimate, ['a','b'])), 2)
        self.assertEqual(estimate('12345'), 2)

    def test_ordinary_control_preserves_owner_instructions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = seed(Path(directory), 'ordinary', 'brownfield')
            for name in ('AGENTS.md', 'CLAUDE.md'):
                self.assertIn('Preserve the existing receipt identifier', (root/name).read_text())

    def test_ordinary_control_preserves_override(self):
        with tempfile.TemporaryDirectory() as directory:
            root = seed(Path(directory), 'ordinary', 'override')
            self.assertIn('Keep receipt processing offline', (root/'AGENTS.override.md').read_text())

if __name__ == '__main__':
    unittest.main()
