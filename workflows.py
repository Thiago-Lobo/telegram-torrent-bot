#!/usr/bin/python

import logging
import jsonpickle
import json
import random
import sqlite_driver
import transmission_driver
import util
import emoji
import telegram_bot
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

####################################################
## Initializers
####################################################

def initialize():
	logger.info('Initializing workflows')
	sqlite_driver.initialize()
	transmission_driver.initialize()

####################################################
## Helpers
####################################################

def generate_torrent_info_message(torrent_data):
	name = torrent_data['name']
	percentage_done = (1.0 - float(torrent_data['leftUntilDone']) / float(torrent_data['totalSize'])) * 100.0
	size = '%.2f' % (float(torrent_data['totalSize'] / (1000.0 * 1000.0 * 1000.0)))
	added = util.timestamp_to_string(util.epoch_to_timestamp(torrent_data['addedDate']))

	message = 'Name: {name}\nSize: {size} GB\nDone: {percentage_done}%\nAdded: {added}'.format(
			name = name,
			percentage_done = percentage_done,
			size = size,
			added = added
		)

	return message

def generate_buttons_for_get_info_message(torrent_hash):
	button_list = [
		InlineKeyboardButton(emoji.emojize(':play_or_pause_button:'), callback_data='%s:%s' % (telegram_bot.CALLBACK_QUERY_PLAY_PAUSE_TORRENT, torrent_hash)),
		InlineKeyboardButton(emoji.emojize(':recycling_symbol:'), callback_data='%s:%s' % (telegram_bot.CALLBACK_QUERY_REFRESH_TORRENT, torrent_hash)),
		InlineKeyboardButton(emoji.emojize(':cross_mark:'), callback_data='%s:%s' % (telegram_bot.CALLBACK_QUERY_DELETE_TORRENT, torrent_hash))
	]

	return InlineKeyboardMarkup(util.build_menu(button_list, n_cols=3))

####################################################
## Workflows
####################################################

def add_torrent_by_magnet_link(username, args):
	result = {
		"worked": False,
		"retry": False,
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
		result['retry'] = True
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
		if torrent['leftUntilDone'] == 0:
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

def get_torrent_information(message, use_id, args):
	result = {
		'retry': False,
		'text': None,
		'reply_markup': None,
		'chat_id': message.chat_id
	}

	username = message.chat_id

	user_torrent_hashes = sqlite_driver.get_torrent_hashes_by_user(username)

	logger.debug('Got %s torrent hashes for username: %s', json.dumps(user_torrent_hashes), username)

	try:
		if not use_id:
			args = transmission_driver.torrent_hash_to_id(args)

		torrent_data = transmission_driver.get_torrent_info_by_id(args[0])[0]

		logger.debug('Torrent hash strings: %s', torrent_data['hashString'])

		if torrent_data['hashString'] in user_torrent_hashes:
			result['reply_markup'] = generate_buttons_for_get_info_message(torrent_data['hashString'])
			result['text'] = generate_torrent_info_message(torrent_data)
		else:
			result['text'] = 'Torrent not found.'
	except transmission_driver.PreallocationException:
		logger.debug('Transmission daemon is preallocating. Aborting workflow.')
		result['text'] = 'Preallocating. Will retry in a few seconds.'
		result['retry'] = True
	except Exception as ex:
		result['text'] = 'Execution error.'
		logging.exception('Error when getting torrent information.')

	return result

####################################################
## Testers
####################################################

def main():
	initialize()
	data = check_completed_torrents()

	print json.dumps(data)

if __name__ == '__main__':
	main()
