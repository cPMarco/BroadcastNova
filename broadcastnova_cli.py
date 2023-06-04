import os
import sys
import getopt
import pathlib
from broadcastnova import process_input_servers, execute_broadcastnova, validate_num_lines


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
    -g    SSH into any VM's matching a provided glob, like *search_term*
    # These also satisfy the requirement, but are tailored for my own workflow
      -s    SSH into only sandbox VM's
      -b    SSH into only binary VM's
      -i    SSH into only idev VM's
    '''.format(script=sys.argv[0], file=FILE)

    print(help_txt)
    sys.exit(1)


def main(argv):
    # Get command line options
    try:
        opts, args = getopt.getopt(argv, 'hvasbiwvg:f:', ['help', 'man'])
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
    print("\nFILE: [{}]".format(FILE))

    if not os.path.isfile(FILE):
        print("\n[error] FILE not found: {}".format(FILE))
        print("[error] Ensure the directory and file exist.")
        usage()

    lines = process_input_servers(opt['input_file'] or FILE, opt['glob_filter'], opt['all_vms'], opt['sandbox_vms'], opt['binary_vms'], opt['idev_vms'])

    if opt['show']:
        if opt['glob_filter']:
            lines = get_lines_with_filter(lines, opt['glob_filter'])
        print('\n'.join(lines))
        sys.exit(0)

    validate_num_lines(lines)

    if not lines:
        sys.exit(1)

    execute_broadcastnova(lines, int(len(lines) ** 0.5) if len(lines) > 3 else len(lines), USERNAME, SCRIPT_NAME)


if __name__ == '__main__':
    main(sys.argv[1:])

