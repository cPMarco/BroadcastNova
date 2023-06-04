# BroadcastNova

Using iTerm2, paste results from 'nova list' into a temp file, then connect to all your VM's at once. Allows you to send them all commands and view all the results in real time.

### Usage

$ Broadcast-list-of-ips.py -h

    Broadcast-list-of-ips.py [-h|-a|-s|-b|-i|-w|-v|-g <glob_pattern>] ( [-f <filepath>] )

    Optional Options:
    -h    This help
    -v    Verbose
    -f    Use custom file for input. Default is:
              ${HOME}/.config/broadcastnova/input-servers.txt
    -w    Show contents of input file, can be combined with -g

    Required Options (only one):
    -a    SSH into all VM's
    -g    SSH into any VM's matching a provided glob, like "*search_term*"
    # These also satify the requirement, but are tailored for my own workflow
      -s    SSH into only sandbox VM's
      -b    SSH into only binary VM's
      -i    SSH into only idev VM's


I use these aliases on my Mac (~/.bash_profile or ~/.zshrc):

    alias broadcast="${HOME}/git/BroadcastNova/Broadcast-list-of-ips.py"
    broadcastpaste() {
        pbpaste > "${HOME}/.config/broadcastnova/input-servers.txt"
    }

### Contribute

* The python3 version is latest and the only one supported.
* If anyone wants to make contributions using bash or perl, check git history, I'd be willing to switch.

### Credit
* From [ramannanda/Broadcast](https://github.com/ramannanda/Broadcast)
* Couple [informative](https://github.com/bikboy/Tim/wiki/AWS-CLI----ITerm2-automation-(Mac)) [pages](https://alvinalexander.com/source-code/mac-os-x/how-run-multiline-applescript-script-unix-shell-script-osascript).
