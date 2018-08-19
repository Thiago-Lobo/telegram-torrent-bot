#!/bin/bash

BOT_NAME='telegram_bot.py'
PID_FILE='bot.pid'

echo "Starting bot: $BOT_NAME"
nohup python telegram_bot.py >/dev/null 2>&1 &

BOT_PID=$!

echo "Storing pid: $BOT_PID" 
echo $BOT_PID > $PID_FILE
