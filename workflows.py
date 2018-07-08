#!/usr/bin/python

import logging
import jsonpickle
import json
import random
import sqlite_driver
import transmission_driver

logger = logging.getLogger(__name__)

def initialize():
	sqlite_driver.initialize()
	transmission_driver.initialize()

def add_torrent_by_magnet_link_worfklow(magnet_link):
	result = {
		"worked": True,
		"should_retry": False,
		"message": ''
	}

	try:
		added_torrent = transmission_driver.add_torrent_magnet_link(args[0])
		row_id = sqlite_driver.insert_torrent_record(added_torrent['hashString'])
		sqlite_driver.insert_torrent_user(row_id, update.message.chat_id)
		bot.send_message(chat_id=update.message.chat_id, text='Torrent "{0}" was added to download queue.'.format(added_torrent['name']))
	except transmission_driver.PreallocationException:
		job_queue.run_once(lambda bot, job: add_magnet(bot, update, job_queue, args), PREALLOCATION_RETRY_SECONDS)
		bot.send_message(chat_id=update.message.chat_id, text='Torrent engine is currently preallocating. Will retry automatically in {0} seconds.'.format(PREALLOCATION_RETRY_SECONDS))
	except Exception as ex:
		logging.exception('Error when adding torrent by magnet link.')
		bot.send_message(chat_id=update.message.chat_id, text='Error when adding torrent by magnet link. Please verify provided link.')

	return result
