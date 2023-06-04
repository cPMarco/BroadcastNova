#!/usr/bin/env python3
import os
import pathlib
import sys
import getopt
import re
import fnmatch
import subprocess

# Constants
FILE = os.environ.get('HOME') + '/.config/broadcastnova/input-servers.txt'
TEMP_FILE = "/tmp/BroadcastNova-IPs.txt"
USERNAME = 'root'
SCRIPT_NAME = pathlib.Path(__file__).parent.resolve()

# Command line options
opt = {
    'input_file': '',
    'all_vms': False,
    'sandbox_vms': False,
    'binary_vms': False,
    'idev_vms': False,
    'show': False,
    'verbose': False,
    'help': False,
    'man': False,
    'glob_filter': None
}

def usage():
    help_txt = '''
    Usage:
      {script} [-h|-a|-s|-b|-i|-w|-v|-g <glob_pattern>] ( [-f <filepath>] )

    Optional Options:
    -h    This help
    -v    Verbose
    -f    Use custom file for input. Default is:
              {file}
    -w    Show contents of input file, can be combined with -g

    Required Options (only one):
    -a    SSH into all VM's
    -g    SSH into any VM's matching a provided glob, like "*search_term*"
    # These also satify the requirement, but are tailored for my own workflow
      -s    SSH into only sandbox VM's
      -b    SSH into only binary VM's
      -i    SSH into only idev VM's
    '''.format(script=SCRIPT_NAME, file=FILE)

    print(help_txt)
    sys.exit(1)

def print_out(text):
    if opt['verbose']:
        print(text)

# Get command line options
try:
    opts, args = getopt.getopt(sys.argv[1:], 'hvasbiwvg:f:', ['help', 'man'])
except getopt.GetoptError:
    usage()

for opt_name, opt_value in opts:
    if opt_name in ('-h', '--help'):
        opt['help'] = True
    elif opt_name == '-v':
        opt['verbose'] = True
    elif opt_name == '-a':
        opt['all_vms'] = True
    elif opt_name == '-s':
        opt['sandbox_vms'] = True
    elif opt_name == '-b':
        opt['binary_vms'] = True
    elif opt_name == '-i':
        opt['idev_vms'] = True
    elif opt_name == '-w':
        opt['show'] = True
    elif opt_name == '-g':
        opt['glob_filter'] = opt_value
    elif opt_name == '-f':
        opt['input_file'] = opt_value
    elif opt_name == '--man':
        opt['man'] = True

# Main
print_out("\nFILE: [{}]".format(FILE))

# Check for Default Arguments (Instance Name)
if not os.path.isfile(FILE):
    print("\n[error] FILE not found: {}".format(FILE))
    print("[error] Ensure the directory and file exist.")
    usage()

with open(FILE, 'r') as fh:
    lines = fh.read().splitlines()

def validate_num_lines(lines):
    lines_with_ips = get_lines_with_ips(lines)
    length_input_file = len(lines)
    if length_input_file != len(lines_with_ips):
        print("\n[error] Input file needs to be a list full of only servers with IP addresses. Each line is checked.\n")
        usage()

def get_lines_with_filter(lines):
    return fnmatch.filter(lines, opt['glob_filter'])

def get_lines_with_ips(lines):
    return [line for line in lines if re.search(r'\d{1,3}(?:\.\d{1,3}){3}', line)]

def get_ips(lines, include=None, exclude=None):
    include = re.compile(include) if include else re.compile(r'.*')
    exclude = re.compile(exclude) if exclude else re.compile(r'^$')
    return [re.sub(r'.+?((\d{1,3}\.){3}\d{1,3}).*', r'\1', line) for line in lines if include.search(line) and not exclude.search(line)]

def get_ips_all(lines):
    return get_ips(lines, exclude='store|manage|verify|tickets')

def get_ips_sandbox(lines):
    return get_ips(lines, include='sand|sb-')

def get_ips_binary(lines):
    return get_ips(lines, exclude='sand|sb-|_sb_|store|manage|verify|tickets')

def get_ips_idev(lines):
    return get_ips(lines, include='store|manage|verify|tickets')

if opt['show']:
    if opt['glob_filter']:
        lines = get_lines_with_filter(lines)
    print('\n'.join(lines))
    sys.exit(0)

validate_num_lines(lines)

if opt['all_vms']:
    ips = get_ips_all(lines)
elif opt['glob_filter']:
    lines = get_lines_with_filter(lines)
    ips = get_ips_all(lines)
elif opt['sandbox_vms']:
    ips = get_ips_sandbox(lines)
elif opt['binary_vms']:
    ips = get_ips_binary(lines)
elif opt['idev_vms']:
    ips = get_ips_idev(lines)
else:
    print("\n[error] type of VM is required but was not found.\n")
    usage()

if opt['glob_filter']:
    lines = fnmatch.filter(lines, opt['glob_filter'])
    ips = get_ips(lines)

print("\nHost IP's found:")
print('\n'.join(ips))

# Check with user to ensure not connecting to wrong servers
print("\nProceed? Type 'y' for yes")
print("[no] ", end='')
proceed_ans = input().strip()
if not re.match(r'^(y|yes|Y|YES)$', proceed_ans):
    print_out("\nExiting...\n")
    sys.exit(1)

# Check if Instances Exist
count = len(ips)
if count == 0:
    print("IP(s) Not Found!")
    sys.exit(0)

# Determine Row / Column Layout
rows = int(count ** 0.5) if count > 3 else count

ips_str = ' '.join(ips)

command = [os.path.join(SCRIPT_NAME, 'scripts/osascript.sh'), '-o', ips_str, '-r', str(rows), '-u', USERNAME]
print("\nRunning:\n", " ".join(command))
subprocess.run(command)

sys.exit(1)
