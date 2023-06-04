import sys
import os
import pathlib
import re
import fnmatch

FILE = os.environ.get('HOME') + '/.config/broadcastnova/input-servers.txt'

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
    -g    SSH into any VM's matching a provided glob, like *search_term*
    # These also satisfy the requirement, but are tailored for my own workflow
      -s    SSH into only sandbox VM's
      -b    SSH into only binary VM's
      -i    SSH into only idev VM's
    '''.format(script=sys.argv[0], file=FILE)


def get_lines_with_filter(lines, glob_filter):
    return fnmatch.filter(lines, glob_filter)


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


def validate_num_lines(lines):
    if not lines:
        print("\n[error] Input file is empty or does not contain valid lines.\n")
        usage()
    lines_with_ips = get_lines_with_ips(lines)
    length_input_file = len(lines)
    if length_input_file != len(lines_with_ips):
        print("\n[error] Input file needs to be a list full of only servers with IP addresses. Each line is checked.\n")
        usage()

# debugm
# def validate_num_lines(lines):
#     lines_with_ips = get_lines_with_ips(lines)
#     length_input_file = len(lines)
#     if length_input_file != len(lines_with_ips):
#         print("\n[error] Input file needs to be a list full of only servers with IP addresses. Each line is checked.\n")
#         usage()


def process_input_file(file):
    with open(file, 'r') as fh:
        lines = fh.read().splitlines()
    return lines


def process_input_servers(file, glob_filter, all_vms, sandbox_vms, binary_vms, idev_vms):
    lines = process_input_file(file)

    if glob_filter:
        lines = get_lines_with_filter(lines, glob_filter)

    if all_vms:
        ips = get_ips_all(lines)
    elif sandbox_vms:
        ips = get_ips_sandbox(lines)
    elif binary_vms:
        ips = get_ips_binary(lines)
    elif idev_vms:
        ips = get_ips_idev(lines)
    else:
        print("\n[error] type of VM is required but was not found.\n")
        return None

    return ips


def execute_broadcastnova(ips, rows, username, script_name):
    ips_str = ' '.join(ips)
    command = [os.path.join(script_name, 'scripts/osascript.sh'), '-o', ips_str, '-r', str(rows), '-u', username]
    print("\nRunning:\n", " ".join(command))
    subprocess.run(command)

