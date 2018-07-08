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
from datetime import datetime, timedelta
from optparse import OptionParser
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from pprint import pprint

BOT_TOKEN = '599359528:AAGj6akAzWX12u16nvOxjxF9cf_go6zncv8'
logger = logging.getLogger(__name__)

TORRENTS_CHECK_PERIOD = 15
PREALLOCATION_RETRY_SECONDS = 60
TELEGRAM_COMMAND_ADD_TORRENT_MAGNET_LINK = 'add_magnet'

# Add Torrent
# Remove Torrent (specific/all)
# Pause Torrent (specific/all)
# Check Torrent (specific/all)
# Alert after torrent is done
# Check seed/leech stats

# def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
#     menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
#     if header_buttons:
#         menu.insert(0, header_buttons)
#     if footer_buttons:
#         menu.append(footer_buttons)
#     return menu

# def echo(bot, update):
# 	bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

# def caps(bot, update, args):
# 	text_caps = ' '.join(args).upper()
# 	bot.send_message(chat_id=update.message.chat_id, text=text_caps)

# def buttons1(bot, update):
	# custom_keyboard = [['TL', 'TR'], ['BL', 'BR']]
	# reply_markup = ReplyKeyboardMarkup(custom_keyboard)
	# bot.send_message(update.message.chat_id, text="Custom keyboard test", reply_markup=reply_markup)

# def buttons(bot, update):
# 	button_list = [	
# 		InlineKeyboardButton("col1", callback_data='a'),
# 		InlineKeyboardButton("col2", callback_data='b'),
# 		InlineKeyboardButton("row 2", callback_data='c')
# 	]

# 	reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
# 	bot.send_message(update.message.chat_id, text="A two-column menu", reply_markup=reply_markup)

# def callback_query_resolver(bot, update):
# 	button_list = [	
# 		InlineKeyboardButton("col1", callback_data='a'),
# 		InlineKeyboardButton("col2", callback_data='b'),
# 		InlineKeyboardButton("row 2", callback_data='c')
# 	]

# 	reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
# 	# pprint(vars(update.callback_query))
# 	# pprint(vars(update.callback_query.message))
# 	bot.answer_callback_query(update.callback_query.id)
# 	bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, text='{0}'.format(update.callback_query.data), reply_markup=reply_markup)
# 	# bot.send_message(chat_id=update.callback_query.message.chat_id, text='{0}'.format(update.callback_query.data))

# def unknown(bot, update):
# 	print update.message.chat_id
# 	bot.send_message(chat_id=update.message.chat_id, text='I don\'t know this command')

####################################################
## Handler Callbacks
####################################################

def add_magnet(bot, update, job_queue, args):
	logger.info('Handling [%s] command - arguments: %s', TELEGRAM_COMMAND_ADD_TORRENT_MAGNET_LINK, json.dumps(args))
	
	result = workflows.add_torrent_by_magnet_link(update.message.chat_id, args)

	if result['should_retry']:
		job_queue.run_once(lambda bot, job: add_magnet(bot, update, job_queue, args), PREALLOCATION_RETRY_SECONDS)

	bot.send_message(chat_id=update.message.chat_id, text=result['message'])

####################################################
## Periodic Jobs
####################################################

def check_completed_torrents(bot, job):
	logger.info('Initializing check_completed_torrents periodic job')

	result = workflows.check_completed_torrents()

	for item in result:
		bot.send_message(chat_id=item['username'], text=item['message'])

####################################################
## Initializers
####################################################

def initialize_logging():
	logging.basicConfig(
		filename='log_telegram_bot.log',
		level=logging.INFO,
		format='%(asctime)s.%(msecs)03d [%(name)25s] %(levelname)-7s %(funcName)s - %(message)s', 
		datefmt='%Y-%m-%d %H:%M:%S'
	)

def initialize_periodic_jobs(job_queue):
	logger.info('Initializing periodic jobs')
	job_queue.run_repeating(check_completed_torrents, interval=TORRENTS_CHECK_PERIOD)

def initialize_bot():
	logger.info('Initializing Telegram Bot')
	updater = Updater(token = BOT_TOKEN)
	dispatcher = updater.dispatcher
	queue = updater.job_queue

	# start_handler = CommandHandler('start', start, pass_job_queue=True)
	# dispatcher.add_handler(start_handler)
	
	# echo_handler = MessageHandler(Filters.text, echo)
	# dispatcher.add_handler(echo_handler)

	# buttons_handler = CommandHandler('buttons', buttons)
	# dispatcher.add_handler(buttons_handler)

	# caps_handler = CommandHandler('caps', caps, pass_args=True)
	# dispatcher.add_handler(caps_handler)

	dispatcher.add_handler(CommandHandler(TELEGRAM_COMMAND_ADD_TORRENT_MAGNET_LINK, add_magnet, pass_args=True, pass_job_queue=True))

	# unknown_handler = MessageHandler(Filters.command, unknown)
	# dispatcher.add_handler(unknown_handler)

	# callback_query_handler = CallbackQueryHandler(callback_query_resolver)
	# dispatcher.add_handler(callback_query_handler)

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
