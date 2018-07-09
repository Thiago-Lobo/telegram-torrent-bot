#!/usr/bin/python

import logging
import jsonpickle
import json
import random
import sqlite_driver
import transmission_driver

logger = logging.getLogger(__name__)

####################################################
## Initializers
####################################################

def initialize():
	logger.info('Initializing workflows')
	sqlite_driver.initialize()
	transmission_driver.initialize()

####################################################
## Workflows
####################################################

def add_torrent_by_magnet_link(username, args):
	result = {
		"worked": False,
		"should_retry": False,
		"message": ''
	}

	logger.info('Starting add_torrent_by_magnet_link workflow with args: %s', json.dumps(args))

	try:
		added_torrent = transmission_driver.add_torrent_magnet_link(args[0])
		row_id = sqlite_driver.insert_torrent_record(added_torrent['hashString'])
		sqlite_driver.insert_torrent_user(row_id, username)
		result['worked'] = True
		result['message'] = 'Torrent "{0}" was added to download queue with ID "{1}".'.format(added_torrent['name'], added_torrent['id'])
	except transmission_driver.PreallocationException:
		result['should_retry'] = True
		result['message'] = 'Torrent engine is currently preallocating. Will retry automatically.'
	except Exception as ex:
		logging.exception('Error when adding torrent by magnet link.')
		result['message'] = 'Error when adding torrent by magnet link.'

	logging.debug('Workflow result: %s', json.dumps(result))

	return result

def check_completed_torrents():
	result = []

	logger.info('Starting check_completed_torrents workflow')

	try:
		transmission_torrents = transmission_driver.get_torrent_info_by_id(transmission_driver.ALL_TORRENTS_STRING)
	except transmission_driver.PreallocationException:
		logger.debug('Transmission daemon is preallocating. Aborting workflow.')
		return result

	unreported_hashes = sqlite_driver.get_unreported_torrents_hashstrings()

	for torrent in transmission_torrents:
		status = torrent['status']
		if status > transmission_driver.get_status_id('downloading'):
			logger.debug('Torrent "%s" with ID "%s" finished downloading.', torrent['name'], torrent['id'])
			if torrent['hashString'] in unreported_hashes:
				logger.debug('Torrent "%s" with ID "%s" is unreported. Will tag it for reporting.', torrent['name'], torrent['id'])
				message = 'Torrent "{0}" with ID "{1}" has finished downloading! Enjoy :)'.format(torrent['name'], torrent['id'])
				usernames = sqlite_driver.get_users_by_torrent_hash(torrent['hashString'])
				for username in usernames:
					result.append({
							'username': username,
							'message': message,
							'hash_string': torrent['hashString']
						})

	logger.debug('Reporting data: %s', json.dumps(result))

	return result

def tag_torrents_as_reported(hash_strings):
	if not isinstance(hash_strings, list):
		hash_strings = [ hash_strings ]

	logger.info('Starting tag_torrents_as_reported workflow with hash_strings: %s', json.dumps(hash_strings))

	for hash_string in hash_strings:
		sqlite_driver.set_torrent_reported(hash_string)

####################################################
## Testers
####################################################		

def main():
	initialize()
	data = check_completed_torrents()

	print json.dumps(data)

if __name__ == '__main__':
	main()
