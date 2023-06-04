#!/usr/bin/env python3
import sys
import os
import re

# Constants
FILE = os.environ.get('HOME') + '/.config/broadcastnova/input-servers.txt'
TEMP_FILE = "/tmp/BroadcastNova-IPs.txt"
USERNAME = 'root'
SCRIPT_NAME = os.path.basename(__file__)

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
    'man': False
}

def usage():
    help_txt = '''
    Usage:
      {script} [-h|-a|-s|-b|-i|-w|-v] ( [-f <filepath>] )

    Optional Options:
    -h    This help
    -v    Cause {script} to be verbose
    -f    Use custom file for input. Default is:
              {file}
    -w    Show contents of input file

    Required Options (only one):
    -a    SSH into all VM's
    -s    SSH into only sandbox VM's
    -b    SSH into only binary VM's
    -i    SSH into only idev VM's
    '''.format(script=SCRIPT_NAME, file=FILE)

    print(help_txt)
    sys.exit(1)

def print_out(text):
    if opt['verbose']:
        print(text)

# Main
print_out("\nFILE: [{}]".format(FILE))

# Check for Default Arguments (Instance Name)
if not os.path.isfile(FILE):
    print("\n[error] FILE not found: {}".format(FILE))
    print("[error] Ensure the directory and file exist.")
    usage()

with open(FILE, 'r') as fh:
    lines = fh.read().splitlines()

if opt['show']:
    print('\n'.join(lines))
    sys.exit(0)

def validate_num_lines(lines):
    lines_with_ips = get_lines_with_ips(lines)
    length_input_file = len(lines)
    if length_input_file != len(lines_with_ips):
        print("\n[error] Input file needs to be a list full of only servers with IP addresses. Each line is checked.\n")
        usage()

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

validate_num_lines(lines)

if opt['all_vms']:
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

print("\nRunning:")
print("{} -o {} -r {} -u {}\n".format(os.path.join(SCRIPT_NAME, 'scripts/osascript.sh'), ips_str, rows, USERNAME))
os.system("{} -o {} -r {} -u {}".format(os.path.join(SCRIPT_NAME, 'scripts/osascript.sh'), ips_str, rows, USERNAME))

sys.exit(1)
