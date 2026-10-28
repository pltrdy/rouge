import configparser
import glob
import json
import os
import subprocess
import sys
import tempfile
from unittest import TestCase


class CliTest(TestCase):
    def test_entry_point_with_unrelated_bin_package(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with tempfile.TemporaryDirectory() as temporary:
            build = os.path.join(temporary, 'build')
            metadata = os.path.join(temporary, 'metadata')
            application = os.path.join(temporary, 'application')
            os.makedirs(metadata)
            os.makedirs(os.path.join(application, 'bin'))
            with open(os.path.join(application, 'bin', '__init__.py'), 'w'):
                pass

            result = subprocess.run(
                [sys.executable, 'setup.py', 'build', '--build-base', build,
                 'egg_info', '--egg-base', metadata],
                cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            entry_points = configparser.ConfigParser()
            entry_points.read(glob.glob(os.path.join(
                metadata, '*.egg-info', 'entry_points.txt')))
            module, function = entry_points['console_scripts']['rouge'].split(':')
            command = [
                sys.executable, '-c',
                'import importlib; getattr(importlib.import_module({!r}), {!r})()'
                .format(module, function),
                '-f', os.path.join(root, 'tests', 'hyp.txt'),
                os.path.join(root, 'tests', 'ref.txt'), '--avg',
            ]
            env = os.environ.copy()
            env['PYTHONPATH'] = os.path.join(build, 'lib')
            control = subprocess.run(command, cwd=temporary, env=env,
                                     capture_output=True, text=True)
            self.assertEqual(control.returncode, 0, control.stderr)
            env['PYTHONPATH'] = os.pathsep.join(
                [application, os.path.join(build, 'lib')])
            collision = subprocess.run(command, cwd=temporary, env=env,
                                       capture_output=True, text=True)
            self.assertEqual(collision.returncode, 0, collision.stderr)
            self.assertEqual(json.loads(control.stdout), json.loads(collision.stdout))
