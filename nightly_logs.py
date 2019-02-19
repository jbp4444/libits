#!/usr/bin/python

# TODO: catch errors when opening output files

import os
import sys
from datetime import datetime
import subprocess
import ssl
import urllib
import urllib2
from cookielib import CookieJar

# # # # # # # # # # # # # # # # # # # #

# basic config settings

config = {
	'basedir': './',
	'df_cmd': '/usr/bin/df',
	'df_args': [
		'-k',
		'--output=file,target,fstype,itotal,iused,iavail,ipcent,size,used,avail,pcent'
	],
	'mount_points': [
		'/srv/perkins/nas/DSPACE',
		'/srv/perkins/nas/DDR',
		'/srv/perkins/nas/RDR',
		'/srv/perkins/nas/DPC-ARCHIVE',
		'/srv/perkins/nas/RL-ARCHIVE'
	],
	'tape_url': 'https://10.136.10.139',
	'tape_username': 'apiuser',
	'tape_password': 'apiAccess',
	'diskfree_threshold': 90,   # percent
	'cleaning_threshold': 90,   # days
	'verbose': 1
}

# # # # # # # # # # # # # # # # # # # #
## # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # #

def tape_api_login( cfg ):
	# curl --insecure --cookie-jar cookies \
	# 	--header "Content-Type: application/json" \
	# 	-d '\
	# 	-v -o output.txt \
	# 	-X POST  https://10.136.10.139/aml/users/login
	data = { "name": cfg['tape_username'], "password": cfg['tape_password'] }
	request = urllib2.Request( cfg['tape_url']+'/aml/users/login', urllib.urlencode(data) )
	response = urllib2.urlopen( request )
	the_page = response.read()
	if( cfg['verbose'] > 10 ):
		print( response.headers )
	if( cfg['verbose'] > 1 ):
		print( the_page )

	# save data for later analysis
	return {
		'response': response,
		'page_data': the_page
	}

def tape_api_edlm( cfg, outfile ):
	# curl --insecure --cookie cookies \
	# -v -o output3.txt \
	# -X GET  https://10.136.10.139/aml/media/edlm
	# curl --insecure --cookie cookies \
	# 	-v -o output5.txt \
	# 	-X GET  https://10.136.10.139/aml/media/reports/edlm
	request = urllib2.Request( cfg['tape_url']+'/aml/media/reports/edlm' )
	response = urllib2.urlopen( request )
	the_page = response.read()
	if( cfg['verbose'] > 10 ):
		print( response.headers )
	if( cfg['verbose'] > 1 ):
		print( the_page )
	
	# write the data to disk
	with open(outfile,'w') as fp:
		fp.write( the_page )

	# save data for later analysis
	return {
		'response': response,
		'page_data': the_page
	}

def tape_api_usage( cfg, outfile ):
	# curl --insecure --cookie cookies \
	# -v -o outputg.txt \
	# -X GET  https://10.136.10.139/aml/media/reports/usage
	request = urllib2.Request( cfg['tape_url']+'/aml/media/reports/usage' )
	response = urllib2.urlopen( request )
	the_page = response.read()
	if( cfg['verbose'] > 10 ):
		print( response.headers )
	if( cfg['verbose'] > 1 ):
		print( the_page )

	# write the data to disk
	with open(outfile,'w') as fp:
		fp.write( the_page )

	# save data for later analysis
	return {
		'response': response,
		'page_data': the_page
	}

def tape_api_partition( cfg, outfile ):
	# TODO: parameterize this function or url-get?  (in case lib_scalar_01 name changes)
	# curl --insecure --cookie cookies \
	# 	-v -o output.txt \
	# 	-X GET  https://10.136.10.139/aml/partition/lib_scalar_01
	request = urllib2.Request( cfg['tape_url']+'/aml/partition/lib_scalar_01' )
	response = urllib2.urlopen( request )
	the_page = response.read()
	if( cfg['verbose'] > 10 ):
		print( response.headers )
	if( cfg['verbose'] > 1 ):
		print( the_page )

	# write the data to disk
	with open(outfile,'w') as fp:
		fp.write( the_page )

	# save data for later analysis
	return {
		'response': response,
		'page_data': the_page
	}

def tape_api_cleaning( cfg, outfile ):
	# TODO: restrict this to last 30 days of data?  threshold-days of data?
	# curl --insecure --cookie cookies \
	# 	-v -o output.txt \
	# 	-X GET  https://10.136.10.139/aml/drives/reports/cleaning
	request = urllib2.Request( cfg['tape_url']+'/aml/drives/reports/cleaning' )
	response = urllib2.urlopen( request )
	the_page = response.read()
	if( cfg['verbose'] > 10 ):
		print( response.headers )
	if( cfg['verbose'] > 1 ):
		print( the_page )

	# write the data to disk
	with open(outfile,'w') as fp:
		fp.write( the_page )

	# save data for later analysis
	return {
		'response': response,
		'page_data': the_page
	}

def get_diskfree( cfg, outfile ):
	output = []
	try:
		# TODO: should we use stderr=stdout?
		cmd = [ cfg['df_cmd'] ]
		cmd.extend( cfg['df_args'] )
		cmd.extend( cfg['mount_points'] )
		output = subprocess.check_output( cmd )
	except subprocess.CalledProcessError as e:
		# TODO: check actual error thrown
		output = [ '* ERROR: diskfree: CalledProcessError :: '+str(e) ]
	except Exception as e:
		# TODO: check actual error thrown
		output = [ '* ERROR: diskfree: other error :: '+str(e) ]

	if( cfg['verbose'] > 10 ):
		print( output )

	# write data to disk
	with open(outfile,'w') as fp:
		for l in output:
			fp.write( l )

	# save data for later analysis
	return {
		'output': output
	}

def create_summary( cfg, data, outfile ):
	# some dumb stuff that might be useful
	pad = ' ' + '.'*80

	with open(outfile,'w') as fp:

		# check diskfree stats
		thresh = cfg['diskfree_threshold']
		fp.write( 'Disk usage stats ... threshold='+str(thresh)+'%\n' )
		try:
			output = data['diskfree']['output'].splitlines()
		except:
			# TODO: verify that output is blank/no lines
			output = []
		firstline = True
		for l in output:
			# skip first line
			if( firstline ):
				firstline = False
				continue
			# find last space in the line
			i = l.rfind(' ')
			j = l.rfind('%')
			val = int( l[i+1:j] )

			k = l.find(' ')

			ar1 = ''
			ar2 = ''
			if( val >= thresh ):
				ar1 = '==>'
				ar2 = '<=='
			
			fp.write( '%3s %-40.40s %2d%% %s\n' % (ar1,l[:k]+pad,val,ar2) )

		fp.write( '\n' )

		# check tape library reports
		# ... yeah, we should parse the XML "for real"
		fp.write( 'Tape usage stats ...\n' )
		total_num_tapes = 0
		total_num_slots = 0
		tapes_with_data = 0
		total_mbytes = 0
		# : first, how many slots in the partition?
		output = data['tape_api_partition']['page_data']
		# :: look for '<storageSlotCount>' block
		i = output.find( '<storageSlotCount>', 0 )
		j = output.find( '</storageSlotCount>', i )
		if( (i<0) and (j<0) ):
			print( "* Warning: no xml for storageSlotCount" )
		elif( ((i<0) and (j>=0)) or ((i>=0) and (j<0)) ):
			print( "* Warning: only got a fragment of xml for storageSlotCount" )
		else:
			total_num_slots = int( output[i+18:j] )

			if( cfg['verbose'] > 10 ):
				print( 'tape slots:', total_num_slots )
		# :: look for '<mediaCount>' block
		i = output.find( '<mediaCount>', 0 )
		j = output.find( '</mediaCount>', i )
		if( (i<0) and (j<0) ):
			print( "* Warning: no xml for mediaCount" )
		elif( ((i<0) and (j>=0)) or ((i>=0) and (j<0)) ):
			print( "* Warning: only got a fragment of xml for mediaCount" )
		else:
			total_num_tapes = int( output[i+12:j] )

			if( cfg['verbose'] > 10 ):
				print( 'tape count:', total_num_tapes )

		# : check tape usage report
		output = data['tape_api_usage']['page_data']
		cursor = 0
		while( True ):
			# look for next '<mediaUsage>' block
			i = output.find( '<mediaUsage>', cursor )
			j = output.find( '</mediaUsage>', i )

			if( (i<0) and (j<0) ):
				break
			elif( ((i<0) and (j>=0)) or ((i>=0) and (j<0)) ):
				print( "* Warning: only got a fragment of xml for mediaUsage" )
			else:
				# look for next '<type>' block
				ci = output.find( '<type>', i )
				cj = output.find( '</type>', ci )
				tape_type = output[ci+6:cj]

				# look for next '<MBwrite>' block
				mbi = output.find( '<MBwrite>', i )
				mbj = output.find( '</MBwrite>', mbi )
				mbval = output[mbi+9:mbj]

				if( tape_type == 'LTO-7' ):
					pass
				elif( tape_type == 'CLN' ):
					pass
				else:
					print( '* Warning: not an LTO-7 tape ['+output[i:j+13]+']' )

				tapes_with_data = tapes_with_data + 1
				total_mbytes = total_mbytes + int(mbval)

				if( cfg['verbose'] > 10 ):
					print( 'tape data:', tapes_with_data, total_mbytes )

			cursor = j + 13

		# write the output file
		fp.write( '    %d tapes with data, totalling %.1f TB  (%.1f TiB)\n' % 
				(tapes_with_data,total_mbytes/1024.0/1024.0,total_mbytes/1000.0/1000.0) )
		fp.write( '    %d unused tapes; %d empty tape-slots (out of %d total slots)\n' %
				(total_num_tapes-tapes_with_data,total_num_slots-total_num_tapes,total_num_slots) )

		# TODO: check cleaning reports ... that each drive has been checked in threshold num of days
		# output = data['tape_api_cleaning']['page_data']
		# cursor = 0
		# while( True ):
		# 	# look for next '<driveCleaning>' block
		# 	i = output.find( '<driveCleaning>', cursor )
		# 	j = output.find( '</driveCleaning>', i )

		# 	if( (i<0) and (j<0) ):
		# 		break
		# 	elif( ((i<0) and (j>=0)) or ((i>=0) and (j<0)) ):
		# 		print( "* Warning: only got a fragment of xml for driveCleaning" )
		# 	else:
		# 		# look for next '<type>' block
		# 		ci = output.find( '<type>', i )
		# 		cj = output.find( '</type>', ci )
		# 		tape_type = output[ci+6:cj]

		# 	cursor = j + 13
		fp.write( '\n* Warning: Tape-cleaning data not processed\n' )

		# TODO: check EDLM report
		fp.write( '\n* Warning: Tape-EDLM data not processed\n' )


# # # # # # # # # # # # # # # # # # # #
## # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # #

if __name__ == '__main__':
	# TODO: put some of this in a config file?

	# TODO: allow cmdline args?
	argc = len( sys.argv )

	# perform some checks on the input values
	if( config['basedir'][-1] != '/' ):
		config['basedir'] = config['basedir'] + '/'

	# make the nightly directory
	datestr = datetime.today().strftime( '%Y%m%d' )
	dirpath = config['basedir'] + datestr
	try:
		os.makedirs( dirpath )
	except OSError as e:
		# dir already exists ... throw a warning
		print( "* Warning: mkdir: OSError :: "+dirpath+' :: '+str(e) )
	except Exception as e:
		print( "* ERROR: mkdir: other error :: "+dirpath+' :: '+str(e) )
		exit( -1 )
	# : and chdir into the new nightly dir
	try:
		os.chdir( dirpath )
	except OSError as e:
		# could not cd into the dir ... permissions issue?
		print( "* ERROR: chdir: OSError :: "+dirpath+' :: '+str(e) )
		exit( -2 )
	except Exception as e:
		print( "* ERROR: chdir: other error :: "+dirpath+' :: '+str(e) )
		exit( -3 )

	config['dirpath'] = dirpath

	# # # # #

	# run the df commands
	data = {}
	data['diskfree'] = get_diskfree( config, 'df_output.txt' )

	# get the raw XML data from the tape lib
	# : first we need to prep the urllib environment
	ssl._create_default_https_context = ssl._create_unverified_context
	cj = CookieJar()
	opener = urllib2.build_opener( urllib2.HTTPCookieProcessor(cj) )
	urllib2.install_opener(opener)
	config['cookie_jar'] = cj

	# : next, we have to login and catch the session cookie
	data['tape_api_login'] = tape_api_login( config )
	# : now we can get the EDLM data
	data['tape_api_edlm'] = tape_api_edlm( config, 'tape_edlm.xml' )
	# : and the usage data
	data['tape_api_usage'] = tape_api_usage( config, 'tape_usage.xml' )
	# : and the usage data
	data['tape_api_cleaning'] = tape_api_cleaning( config, 'tape_cleaning.xml' )
	# : and the partition info
	data['tape_api_partition'] = tape_api_partition( config, 'tape_partition.xml' )

	create_summary( config, data, 'summary.txt' )
