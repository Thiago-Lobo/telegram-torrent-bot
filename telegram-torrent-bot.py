#!/usr/bin/python

import sys
import os
import re
import json
import subprocess
import time
import transmissionrpc
from datetime import datetime, timedelta
from optparse import OptionParser
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from pprint import pprint

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text='Hello Telegram world!')

def echo(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

def caps(bot, update, args):
	text_caps = ' '.join(args).upper()
	bot.send_message(chat_id=update.message.chat_id, text=text_caps)

# def buttons1(bot, update):
	# custom_keyboard = [['TL', 'TR'], ['BL', 'BR']]
	# reply_markup = ReplyKeyboardMarkup(custom_keyboard)
	# bot.send_message(update.message.chat_id, text="Custom keyboard test", reply_markup=reply_markup)

def buttons(bot, update):
	button_list = [	
		InlineKeyboardButton("col1", callback_data='a'),
		InlineKeyboardButton("col2", callback_data='b'),
		InlineKeyboardButton("row 2", callback_data='c')
	]

	reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
	bot.send_message(update.message.chat_id, text="A two-column menu", reply_markup=reply_markup)

def callback_query_resolver(bot, update):
	button_list = [	
		InlineKeyboardButton("col1", callback_data='a'),
		InlineKeyboardButton("col2", callback_data='b'),
		InlineKeyboardButton("row 2", callback_data='c')
	]

	reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
	# pprint(vars(update.callback_query))
	# pprint(vars(update.callback_query.message))
	bot.answer_callback_query(update.callback_query.id)
	bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, text='{0}'.format(update.callback_query.data), reply_markup=reply_markup)
	# bot.send_message(chat_id=update.callback_query.message.chat_id, text='{0}'.format(update.callback_query.data))

def unknown(bot, update):
	print update.message.chat_id
	bot.send_message(chat_id=update.message.chat_id, text='I don\'t know this command')

def callback_minute(bot, job):
	bot.send_message(chat_id=58880229, text='Every 60 seconds!')

def main():
	updater = Updater(token = '599359528:AAGj6akAzWX12u16nvOxjxF9cf_go6zncv8')
	dispatcher = updater.dispatcher
	queue = updater.job_queue
	

	start_handler = CommandHandler('start', start)
	dispatcher.add_handler(start_handler)
	
	echo_handler = MessageHandler(Filters.text, echo)
	dispatcher.add_handler(echo_handler)

	buttons_handler = CommandHandler('buttons', buttons)
	dispatcher.add_handler(buttons_handler)

	caps_handler = CommandHandler('caps', caps, pass_args=True)
	dispatcher.add_handler(caps_handler)

	unknown_handler = MessageHandler(Filters.command, unknown)
	dispatcher.add_handler(unknown_handler)

	callback_query_handler = CallbackQueryHandler(callback_query_resolver)
	dispatcher.add_handler(callback_query_handler)

	print 'Starting to poll...'

	updater.start_polling()
	updater.idle()

	# job_minute = queue.run_repeating(callback_minute, interval=60, first=0)


if __name__ == '__main__':
	main()
