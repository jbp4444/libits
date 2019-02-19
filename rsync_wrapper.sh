#!/bin/bash

# from:  https://www.xarg.org/2009/10/write-a-pid-file-in-bash/

# settings:
pidfile='./pidfile'
cmdexe='sleep'
cmdargs='100'

# # # # # # # # # # # # # # # # # # # #
 # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # #

pid=`cat $pidfile`

restart=0
if [ -z "$pid" ]; then
	echo Pidfile is empty ... restarting
	restart=1
else
	if [ -e /proc/$pid ]; then
		if [ -n /proc/$pid/exe ]; then
			echo Pidfile found and is valid ... skipping
		else
			echo Pidfile found but no exe ... restarting
			restart=1
		fi
	else
		echo Pidfile found but no exe-dir ... restarting
		restart=1
	fi
fi

if [ $restart -eq 1 ]; then
	echo Restarting [$cmdexe $cmdargs]
	(($cmdexe $cmdargs) & echo $! > $pidfile &)
fi
