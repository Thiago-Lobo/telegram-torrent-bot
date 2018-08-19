#!/usr/bin/python

import sys
import os
import re
import json
import subprocess
import time
import transmission_driver
import workflows
import logging
import util
import traceback
import emoji
from datetime import datetime, timedelta
from optparse import OptionParser
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


API_KEY_FILE = 'telegram_api.key'

logger = logging.getLogger(__name__)

TORRENTS_CHECK_PERIOD = 60
PREALLOCATION_RETRY_SECONDS = 60
TELEGRAM_COMMAND_ADD_TORRENT_MAGNET_LINK = 'add_magnet'
TELEGRAM_COMMAND_GET_TORRENT_INFO = 'get_info'

CALLBACK_QUERY_PLAY_PAUSE_TORRENT = 'cbq_play_pause_torrent'
CALLBACK_QUERY_REFRESH_TORRENT = 'cbq_refresh_torrent'
CALLBACK_QUERY_DELETE_TORRENT = 'cbq_delete_torrent'

####################################################
## Helpers
####################################################

def generate_buttons_for_get_info_message():
	button_list = [
		InlineKeyboardButton(emoji.emojize(':play_or_pause_button:'), callback_data=CALLBACK_QUERY_PLAY_PAUSE_TORRENT),
		InlineKeyboardButton(emoji.emojize(':recycling_symbol:'), callback_data=CALLBACK_QUERY_PLAY_PAUSE_TORRENT),
		InlineKeyboardButton(emoji.emojize(':cross_mark:'), callback_data=CALLBACK_QUERY_PLAY_PAUSE_TORRENT)
	]

	return InlineKeyboardMarkup(util.build_menu(button_list, n_cols=3))

####################################################
## Callback query resolver
####################################################

def callback_query_resolver(bot, update):
	# bot.answer_callback_query(update.callback_query.id)
	# bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, text='{0}'.format(update.callback_query.data))
	# bot.send_message(chat_id=update.callback_query.message.chat_id, text='{0}'.format(update.callback_query.data))

	callback_query_data = update.callback_query.data

	if callback_query_data == CALLBACK_QUERY_REFRESH_TORRENT:
		a = 2
	elif callback_query_data == CALLBACK_QUERY_REFRESH_TORRENT:
		a = 2
	elif callback_query_data == CALLBACK_QUERY_DELETE_TORRENT:
		a = 2
	else:
		a = 2

####################################################
## Handler Callbacks
####################################################

def unknown(bot, update, job_queue, args):
	bot.send_message(chat_id=update.message.chat_id, text='Unknown command.')

def add_magnet(bot, update, job_queue, args):
	logger.info('Handling [%s] command - arguments: %s', TELEGRAM_COMMAND_ADD_TORRENT_MAGNET_LINK, json.dumps(args))
	
	result = workflows.add_torrent_by_magnet_link(update.message.chat_id, args)

	if result['retry']:
		job_queue.run_once(lambda bot, job: add_magnet(bot, update, job_queue, args), PREALLOCATION_RETRY_SECONDS)

	bot.send_message(chat_id=update.message.chat_id, text=result['message'])

def get_info(bot, update, job_queue, args):
	logger.info('Handling [%s] command - arguments: %s', TELEGRAM_COMMAND_GET_TORRENT_INFO, json.dumps(args))
	
	result = workflows.get_torrent_information(update.message.chat_id, args)

	if result['retry']:
		job_queue.run_once(lambda bot, job: get_info(bot, update, job_queue, args), PREALLOCATION_RETRY_SECONDS)
	elif result['data']:
		reply_markup = generate_buttons_for_get_info_message()
		bot.send_message(chat_id=update.message.chat_id, text=result['data'][0], reply_markup=reply_markup)
	else:
		bot.send_message(chat_id=update.message.chat_id, text='No torrent found with the provided ID.')

####################################################
## Periodic Jobs
####################################################

def check_completed_torrents(bot, job):
	logger.info('Initializing check_completed_torrents periodic job')

	result = workflows.check_completed_torrents()

	for item in result:
		logger.debug('Sending message: "%s" to username "%s"', item['message'], item['username'])
		
		message_sent = None
		message_sent = bot.send_message(chat_id=item['username'], text=item['message'])
		
		if message_sent:
			workflows.tag_torrents_as_reported(item['hash_string'])

####################################################
## Initializers
####################################################

def initialize_logging():
	logging.basicConfig(
		filename='log_telegram_bot.log',
		level=logging.DEBUG,
		format='%(asctime)s.%(msecs)03d [%(name)25s] %(levelname)-7s %(funcName)s - %(message)s', 
		datefmt='%Y-%m-%d %H:%M:%S'
	)

def initialize_periodic_jobs(job_queue):
	logger.info('Initializing periodic jobs')
	job_queue.run_repeating(check_completed_torrents, interval=TORRENTS_CHECK_PERIOD)

def initialize_bot():
	logger.info('Initializing Telegram Bot')

	k = open(API_KEY_FILE, 'r')

	updater = Updater(token = k.readlines()[0].strip())
	dispatcher = updater.dispatcher
	queue = updater.job_queue
	
	# buttons_handler = CommandHandler('buttons', buttons)
	# dispatcher.add_handler(buttons_handler)

	dispatcher.add_handler(CommandHandler(TELEGRAM_COMMAND_ADD_TORRENT_MAGNET_LINK, add_magnet, pass_args=True, pass_job_queue=True))
	dispatcher.add_handler(CommandHandler(TELEGRAM_COMMAND_GET_TORRENT_INFO, get_info, pass_args=True, pass_job_queue=True))
	dispatcher.add_handler(MessageHandler(Filters.command, unknown))

	callback_query_handler = CallbackQueryHandler(callback_query_resolver)
	dispatcher.add_handler(callback_query_handler)

	initialize_periodic_jobs(queue)
	
	updater.start_polling()
	updater.idle()

def func0():
	transmission_driver.add_torrent_magnet_link('magnet:?xt=urn:btih:45740f0889a82645dd8a1d5bc50eecedf5e79f47&dn=The.Death.of.Superman.2018.1080p.WEB-DL.DD5.1.H264-FGT&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2710&tr=udp%3A%2F%2F9.rarbg.to%3A2710')

def func1():
	transmission_driver.remove_torrent([1, 2])

def func2():
	transmission_driver.pause_torrent('all')

def func3():
	transmission_driver.resume_torrent([10, 11])

def func4():
	print transmission_driver.get_free_space()

def func5():
	print json.dumps(transmission_driver.get_session_info(), indent=2)

def func6():
	print json.dumps(transmission_driver.get_session_stats(), indent=2)

def func7():
	result = transmission_driver.get_torrent_info_by_id([18])
	for entry in result:
		print json.dumps(entry, indent=2)

def func8():
	print len(transmission_driver.get_torrent_info('all'))

def func9():
	transmission_driver.set_session_property(speed_limit_up_enabled=True, speed_limit_up=10)

def func10():
	transmission_driver.set_session_property(speed_limit_up_enabled=True, speed_limit_up=400)

def func11():
	result = transmission_driver.get_torrent_info_by_hash('45740f0889a82645dd8a1d5bc50eecedf5e79f47')
	for entry in result:
		print json.dumps(entry, indent=2)

def func12():
	transmission_driver.pause_torrent_by_hash('45740f0889a82645dd8a1d5bc50eecedf5e79f47')

def func13():
	transmission_driver.resume_torrent_by_hash('45740f0889a82645dd8a1d5bc50eecedf5e79f47')

def main():
	initialize_logging()
	workflows.initialize()
	initialize_bot()

if __name__ == '__main__':
	main()
