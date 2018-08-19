#!/bin/bash

BOT_NAME='telegram_bot.py'
PID_FILE='bot.pid'

echo "Stopping bot: $BOT_NAME"
kill -9 $(cat $PID_FILE)
rm $PID_FILE
