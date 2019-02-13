#!/usr/bin/python

import os
import sys
import subprocess
import ssl
import urllib
import urllib2
from cookielib import CookieJar

df_cmd = '/usr/bin/df'
df_args = [
	'-k',
	 '--output=file,target,fstype,itotal,iused,iavail,ipcent,size,used,avail,pcent'
]
mount_points = [
	'/srv/perkins/nas/DSPACE',
	'/srv/perkins/nas/DDR',
	'/srv/perkins/nas/RDR',
	'/srv/perkins/nas/DPC-ARCHIVE',
	'/srv/perkins/nas/RL-ARCHIVE'
]

tape_url = 'https://10.136.10.139'

# # # # # # # # # # # # # # # # # # # #
## # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # #

def tape_api_login():
	# curl --insecure --cookie-jar cookies \
	# 	--header "Content-Type: application/json" \
	# 	-d '\
	# 	-v -o output.txt \
	# 	-X POST  https://10.136.10.139/aml/users/login
	data = { "name":"apiuser", "password":"apiAccess" }
	request = urllib2.Request( tape_url+'/aml/users/login', urllib.urlencode(data) )
	response = urllib2.urlopen( request )
	the_page = response.read()
	print( response.headers )
	print( the_page )

def tape_api_edlm( outfile ):
	# curl --insecure --cookie cookies \
	# -v -o output3.txt \
	# -X GET  https://10.136.10.139/aml/media/edlm
	# curl --insecure --cookie cookies \
	# 	-v -o output5.txt \
	# 	-X GET  https://10.136.10.139/aml/media/reports/edlm
	request = urllib2.Request( tape_url+'/aml/media/reports/edlm' )
	response = urllib2.urlopen( request )
	the_page = response.read()
	print( response.headers )
	print( the_page )
	with open(outfile,'w') as fp:
		fp.write( the_page )

def tape_api_usage( outfile ):
	# curl --insecure --cookie cookies \
	# -v -o outputg.txt \
	# -X GET  https://10.136.10.139/aml/media/reports/usage
	request = urllib2.Request( tape_url+'/aml/media/reports/usage' )
	response = urllib2.urlopen( request )
	the_page = response.read()
	print( response.headers )
	print( the_page )
	with open(outfile,'w') as fp:
		fp.write( the_page )

def get_diskfree( mountpts, outfile ):
	output = []
	try:
		# TODO: should we use stderr=stdout?
		cmd = [ df_cmd ]
		cmd.extend( df_args )
		cmd.extend( mountpts )
		print( ' '.join(cmd) )
		output = subprocess.check_output( cmd )
	except subprocess.CalledProcessError as e:
		# TODO: check actual error thrown
		output = [ '* ERROR: subproc error :: '+str(e) ]
	except Exception as e:
		# TODO: check actual error thrown
		output = [ '* ERROR: other error :: '+str(e) ]

	# print( output )
	# TODO: check for outputs > 90% or 95% ??

	with open(outfile,'w') as fp:
		for l in output:
			fp.write( l )

# # # # # # # # # # # # # # # # # # # #
## # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # #

if __name__ == '__main__':
	# TODO: put some of this in a config file?

	# TODO: allow cmdline args?
	argc = len( sys.argv )

	# make the nightly directory

	# chdir into the new nightly dir

	# run the df commands
	get_diskfree( mount_points, 'df_output.txt' )

	# get the raw XML data from the tape lib
	# : first we need to prep the urllib environment
	ssl._create_default_https_context = ssl._create_unverified_context
	cj = CookieJar()
	opener = urllib2.build_opener( urllib2.HTTPCookieProcessor(cj) )
	urllib2.install_opener(opener)
	# : next, we have to login and catch the session cookie
	tape_api_login()
	# : now we can get the EDLM data
	tape_api_edlm( 'tape_edlm.xml' )
	# : and finally, we can get the usage data
	tape_api_usage( 'tape_usage.xml' )
	