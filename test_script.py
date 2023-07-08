import unittest
from unittest.mock import patch
from io import StringIO
import sys
import os
import tempfile
import shutil
import re
import fnmatch
import subprocess
from Broadcast_Launch import *

class TestScript(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b'192.168.0.1\n192.168.0.2\n')
        self.temp_file.close()

    def tearDown(self):
        # Remove the temporary file
        os.remove(self.temp_file.name)

    def test_get_lines_with_filter(self):
        lines = ['test.txt', 'file.txt', 'data.csv']
        opt['glob_filter'] = '*.txt'
        filtered_lines = get_lines_with_filter(lines)
        self.assertEqual(filtered_lines, ['test.txt', 'file.txt'])

    def test_get_lines_with_ips(self):
        lines = ['192.168.0.1', 'not_an_ip', '192.168.0.2']
        lines_with_ips = get_lines_with_ips(lines)
        self.assertEqual(lines_with_ips, ['192.168.0.1', '192.168.0.2'])

    def test_get_ips_all(self):
        lines = ['192.168.0.1', 'sandbox-vm', '192.168.0.2', 'binary-vm']
        ips = get_ips_all(lines)
        self.assertEqual(ips, ['192.168.0.1', '192.168.0.2'])

    def test_get_ips_sandbox(self):
        lines = ['192.168.0.1', 'sandbox-vm', '192.168.0.2', 'binary-vm']
        ips = get_ips_sandbox(lines)
        self.assertEqual(ips, ['sandbox-vm'])

    def test_get_ips_binary(self):
        lines = ['192.168.0.1', 'sandbox-vm', '192.168.0.2', 'binary-vm']
        ips = get_ips_binary(lines)
        self.assertEqual(ips, ['binary-vm'])

    def test_get_ips_idev(self):
        lines = ['192.168.0.1', 'store-vm', '192.168.0.2', 'idev-vm']
        ips = get_ips_idev(lines)
        self.assertEqual(ips, ['store-vm', 'idev-vm'])

    def test_validate_num_lines(self):
        lines = ['192.168.0.1', 'not_an_ip', '192.168.0.2']
        with patch('sys.stdout', new=StringIO()) as fake_out:
            validate_num_lines(lines)
            output = fake_out.getvalue().strip()
            self.assertIn('Input file needs to be a list full of only servers with IP addresses', output)

    @patch('sys.stdout', new=StringIO())
    def test_usage(self, mock_stdout):
        usage()
        output = mock_stdout.getvalue().strip()
        self.assertIn('Usage:', output)

    @patch('sys.stdout', new=StringIO())
    def test_print_out(self, mock_stdout):
        print_out('Test message')
        output = mock_stdout.getvalue().strip()
        self.assertEqual(output, 'Test message')

    def test_main(self):
        opt['input_file'] = self.temp_file.name
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with patch('builtins.input', return_value='y'):
                main()
                output = fake_out.getvalue().strip()
                self.assertIn('Host IP\'s found:', output)

if __name__ == '__main__':
    unittest.main()
