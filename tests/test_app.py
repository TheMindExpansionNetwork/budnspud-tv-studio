import json
import subprocess
import sys
import time
import unittest
import urllib.request
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / 'app'

class AppTest(unittest.TestCase):
    def test_actual_workflow_contract(self):
        graph = json.loads((APP / 'workflow.json').read_text())
        self.assertEqual(graph['136']['class_type'], 'MiniMaxH3ReferenceToVideo')
        self.assertEqual(graph['136']['inputs']['ref_images.ref_image_0'], ['137', 0])
        self.assertEqual(graph['136']['inputs']['ref_images.ref_image_1'], ['149', 0])
        self.assertEqual(graph['136']['inputs']['prompt'], ['138', 0])
        self.assertEqual(graph['130']['inputs']['fps'], 24)
        self.assertIn('yellow propeller plane', graph['138']['inputs']['value'])
    def test_server_serves_actual_files_and_security_header(self):
        proc = subprocess.Popen([sys.executable, str(APP / 'server.py'), '--port', '0'], stdout=subprocess.PIPE, text=True)
        try:
            address = proc.stdout.readline().strip().split()[-1]
            with urllib.request.urlopen(address, timeout=5) as response:
                html = response.read().decode(); self.assertIn('Give it a story', html)
                self.assertIn("default-src 'self'", response.headers['Content-Security-Policy'])
            with urllib.request.urlopen(address + 'workflow.json', timeout=5) as response:
                self.assertEqual(json.load(response)['136']['class_type'], 'MiniMaxH3ReferenceToVideo')
        finally:
            proc.terminate(); proc.wait(timeout=5); proc.stdout.close()

if __name__ == '__main__': unittest.main()
