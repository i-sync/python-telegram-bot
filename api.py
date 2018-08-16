#!/usr/bin/env python

import telegram
import telegram.utils.request
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
import logging
import json
import common
from datetime import datetime
import sync
import os.path


logging.basicConfig(filename = os.path.join(common.root_path, 'log'), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


req = telegram.utils.request.Request(proxy_url= common.proxy)
bot = telegram.Bot(common.token, request= req)
#bot = telegram.Bot(common.token)
sync_file = sync.Sync()

#BOT = telegram.Bot(common.TOKEN)

#log = logging.Logger(__name__)

def command_process(bot, update):
    #print(type(update))
    text = update.message.text
    logging.info(text)
    if text.startswith('/help') or text.startswith('/start'):
        bot.send_message(chat_id=update.message.chat_id, text= common.command_str)
    elif text.startswith('/weather'):
        bot.send_message(chat_id=update.message.chat_id, text= common.get_weather())
    elif text.startswith('/gif'):
        url = common.get_random_gif()
        if url is None:
            bot.send_message(chat_id=update.message.chat_id, text= 'get random gif failed, please try again later...')
        else:
            bot.send_video(chat_id=update.message.chat_id, video = url)
    elif text.startswith('/joke'):
        bot.send_message(chat_id=update.message.chat_id, text= common.get_random_joke())
    #elif text.startswith('/message'):
    #    bot.send_message(chat_id=update.message.chat_id, text = json.dumps(update.message))
    #    logging.info(update.message)
    elif text.startswith('/me'):
        bot_obj = bot.get_me()
        bot_info = {'id': bot_obj.id, 'username': bot_obj.username, 'first_name': bot_obj.first_name, 'last_name': bot_obj.last_name, 'type': bot_obj.type}
        bot.send_message(chat_id=update.message.chat_id, text= json.dumps(bot_info))
    else:
        bot.send_message(chat_id= update.message.chat_id, text = 'sorry, i can\'t understand what\'s your mean...')


def text_process(bot, update):
    logging.info(update.message)
    #print(update.message.text)
    bot.send_message(chat_id= update.message.chat_id, text = update.message.text)


def photo_process(bot, update):
    photo = update.message.photo[-1]
    file = bot.get_file(photo.file_id)
    #logging.info(file.file_path)
    filename = '{}-{}.{}'.format(datetime.today().strftime('%Y%m%d-%H%M%S'), photo.file_id, file.file_path.split('.')[-1])
    filepath = '{}/{}'.format(common.photo_path, filename)
    #print(filepath, file.file_path)
    with open(filepath, 'wb') as f:
        file.download(out = f)
    bot.send_photo(chat_id= update.message.chat_id, photo= photo.file_id)

def audio_process(bot, update):
    audio = update.message.audio if update.message.audio else update.message.voice
    file = bot.get_file(audio.file_id)
    #logging.info(file)

    #filename = '{}-{}.{}'.format(datetime.today().strftime('%Y%m%d-%H%M%S'), audio.file_id, file.file_path.split('.')[-1])
    filename = '{}-{}.oga'.format(datetime.today().strftime('%Y%m%d-%H%M%S'), audio.file_id)
    filepath = '{}/{}'.format(common.voice_path, filename)
    #print(filepath, file.file_path)
    with open(filepath, 'wb') as f:
        file.download(out = f)

    #sync file
    sync_file.enter(filename)

    bot.send_message(chat_id= update.message.chat_id, text = 'Thanks, we have received your voice...')

def video_process(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Thank for your message...')

def default_process(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Thank for your message...')



def start():
    updater = Updater(bot = bot)

    updater.start_polling()

    dispacther = updater.dispatcher

    #handler
    command_handler = CommandHandler(common.command_list, command_process)
    text_handler = MessageHandler(Filters.text, text_process)
    photo_handler = MessageHandler(Filters.photo, photo_process)
    audio_handler = MessageHandler(Filters.audio | Filters.voice | Filters.forwarded & Filters.audio | Filters.forwarded & Filters.voice, audio_process)
    video_handler = MessageHandler(Filters.video, video_process)

    dispacther.add_handler(command_handler)
    dispacther.add_handler(text_handler)
    dispacther.add_handler(photo_handler)
    dispacther.add_handler(audio_handler)
    dispacther.add_handler(video_handler)

if __name__ == '__main__':
    start()