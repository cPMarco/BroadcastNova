#!/bin/bash

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

# Get the options
while getopts ":ho:r:u:" option; do
  case ${option} in
    h ) usage ;;
    o ) HOSTS=$OPTARG ;;
    r ) ROWS=$OPTARG ;;
    u ) USERNAME=$OPTARG ;;
    \? )
      echo "Invalid Option: -$OPTARG" 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

# Start Terminal
osascript <<EOF
tell application "iTerm" to activate
tell application "System Events" to tell process "iTerm" to keystroke "n" using command down
EOF

# Interate through Instances / Results
i=0
for HOST in $HOSTS; do

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

    # debug
    # osascript -e 'tell application "System Events" to tell process "iTerm" to keystroke "ssh -i '"$KEYPAIR"' '"$USERNAME"'@'"$HOST"'"'
    osascript -e 'tell application "System Events" to tell process "iTerm" to keystroke "ssh '"$USERNAME"'@'"$HOST"'"'
	osascript -e 'tell application "System Events" to tell process "iTerm" to key code 52'

    i=$(( $i + 1 ))
done

# Broadcast
osascript -e 'tell application "System Events" to tell process "iTerm" to keystroke "i" using {option down, command down}'
exit 0
