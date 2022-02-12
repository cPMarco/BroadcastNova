#!/bin/bash

# https://github.com/ramannanda/Broadcast
# https://github.com/bikboy/Tim/wiki/AWS-CLI----ITerm2-automation-(Mac)
# https://starkandwayne.com/blog/bash-for-loop-over-json-array-using-jq/
# https://alvinalexander.com/source-code/mac-os-x/how-run-multiline-applescript-script-unix-shell-script-osascript

# If I'm gona redo all that prunning again, here's the start
# nova list --fields 'name','created','status','networks','metadata'
FILE="${HOME}/.config/broadcastnova/input-servers.txt"
TEMP_FILE="/tmp/BroadcastNova-IPs.txt"
USERNAME='root'

usage() {
    echo
    echo "Usage: $(basename $0) [-h|-a|-s|-b|-i|-v] ( [-f <filepath>] )"
    echo
    echo "-h This help"
    echo
    echo "-a SSH into all VM's"
    echo "-s SSH into only sandbox VM's"
    echo "-b SSH into only binary VM's"
    echo "-i SSH into only idev VM's"
    echo
    echo "-v Cause $(basename $0) to be verbose"
    echo "-f Use custom file for input.  Default is ${FILE}."
    echo

	exit 1;
}

print_if_verbose() {
    if [ ${VERBOSE} ]; then
        echo "$1"
    fi
}

# Get the options
while getopts ":f:hasbiv" option; do
  case ${option} in
    h ) usage ;;
    v ) VERBOSE='true' ;;
    f ) FILE="${OPTARG}" ;;
    a ) TYPE='all_vms' ;;
    s ) TYPE='sandbox_vms' ;;
    b ) TYPE='binary_vms' ;;
    i ) TYPE='idev_vms' ;;
    \? )
      echo "Invalid Option: -$OPTARG" 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

print_if_verbose "FILE: [$FILE]"
print_if_verbose "TYPE: [$TYPE]"

# Check for Default Arguments (Instance Name)
if [[ -z "${FILE}" ]] || [[ ! -r "${FILE}" ]]; then
    echo -e "\n[error] FILE not found: $FILE"
    echo "[error] Ensure the directory and file exist."
    usage
fi

length_input_file=$( wc -l $FILE | awk '{print $1}' )
lines_with_ips=$( cat $FILE | \grep -E '([[:digit:]]{1,3}\.){3}[[:digit:]]{1,3}' | wc -l )
if [ $length_input_file -ne $lines_with_ips ]; then
    echo -e "\n[error] Input file needs to be a list full of only servers with IP addresses. Each line is checked.\n"
    usage
fi

if [ "$TYPE" == "all_vms" ]; then
    \egrep -iv "store|manage|verify|tickets" $FILE | \awk '{print $10}' > $TEMP_FILE
elif [ "$TYPE" == "sandbox_vms" ]; then
    \egrep -i "sand|sb-" $FILE | \awk '{print $10}' > $TEMP_FILE
elif [ "$TYPE" == "binary_vms" ]; then
    \egrep -iv "sand|sb-|_sb_|store|manage|verify|tickets" $FILE | \awk '{print $10}' > $TEMP_FILE
elif [ "$TYPE" == "idev_vms" ]; then
    \egrep -i "store|manage|verify|tickets" $FILE | \awk '{print $10}' > $TEMP_FILE
fi

if [ -z "$TYPE" ]; then
    echo -e "\n[error] TYPE not found: $TYPE\n"
    usage
fi

# Get IP's from a file
declare -a HOSTS=( $( cat $TEMP_FILE ) );
echo -e "\nHost IP's found: ${HOSTS[@]}\n"

# Check with user to ensure not connecting to wrong servers
echo "Proceed? Type 'y' for yes"
echo -n "[no] "
read proceed_ans
if [[ ! "$proceed_ans" =~ "y" ]]; then
    print_if_verbose "Exiting..."
    exit
fi

# Check if Instances Exist
COUNT=${#HOSTS[@]}
if [ "$COUNT" = "" ] || [ $COUNT == 0 ]; then
	echo "IP(s) Not Found!"
	exit 1
fi

# Determine Row / Column Layout
if [ $COUNT > 3 ]; then
	ROWS=$(awk -v x=$COUNT 'BEGIN{printf "%3.0f\n", sqrt(x)}')
else
	ROWS=$COUNT
fi

# Start Terminal
osascript <<EOF
tell application "iTerm" to activate
tell application "System Events" to tell process "iTerm" to keystroke "n" using command down
EOF


# Interate through Instances / Results
i=0
for HOST in ${HOSTS[@]}; do

    KEYPAIR="$HOME/.ssh/animal9"
    MOD=$(($i%$ROWS))

    if (( $i < $ROWS )); then
    	# First Column - Split Horizontal to Init First of Each Row
    	if [[ $i != 0 ]]; then
    		osascript -e 'tell application "System Events" to tell process "iTerm" to keystroke "d" using {shift down, command down}'
    	fi
    else
    	if [[ $MOD == 0 ]]; then
    		# Loop Back Up to Top
    		for ((j=1;j<$ROWS;j++)); do
		    	osascript -e 'tell application "System Events" to tell process "iTerm" to key code 126 using {option down, command down}'
			done
    	else
    		# Move Left / Move Down
    		osascript -e 'tell application "System Events" to tell process "iTerm" to key code 123 using {option down, command down}'
    		osascript -e 'tell application "System Events" to tell process "iTerm" to key code 125 using {option down, command down}'
    	fi
    	# Split Vertical
		osascript -e 'tell application "System Events" to tell process "iTerm" to keystroke "d" using command down'
    fi

    osascript -e 'tell application "System Events" to tell process "iTerm" to keystroke "ssh -i '"$KEYPAIR"' '"$USERNAME"'@'"$HOST"'"'
	osascript -e 'tell application "System Events" to tell process "iTerm" to key code 52'

    i=$(( $i + 1 ))
done

# Broadcast
osascript -e 'tell application "System Events" to tell process "iTerm" to keystroke "i" using {option down, command down}'
exit 0

# I got a lot of this from:
# https://github.com/ramannanda/Broadcast
#
# I think I can use it legally as long as I keep this text with it, right?
#
# MIT License
#
# Copyright (c) 2019 Raman Nanda
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
