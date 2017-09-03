#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

import os
import os.path
import telegram
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

token = '23563463:xxx'
group_info = {'id': -21434, 'name': 'Raspberry Group'}

bot = telegram.Bot(token)
#bot.send_message(chat_id= group_info['id'], text='testing, from  pi')
file_path = './files/send'
backup_path = './files/backup'

class MyFileSystemEventHandler(FileSystemEventHandler):

    def __init__(self, fn):
        super().__init__()
        self.fn = fn
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".m4a"):
            logging.info("detect new file created...")
            self.fn(event.src_path)


def send_message(real_path):
    if not os.path.exists(real_path):
        logging.info('{} file not found, return...'.format(real_path))
        return
    bot.send_voice(chat_id = group_info['id'], voice = open(real_path, 'rb'))
    logging.info('{}, send file finish...'.format(real_path))
    #dest_file = os.path.join(os.path.abspath(backup_path), os.path.basename(real_path))
    #logging.info('\nsource:{}\ndest:{}'.format(real_path, dest_file))
    #os.rename(real_path, dest_file)

if __name__ == '__main__':
    real_path = os.path.abspath(file_path)
    #logging.info(real_path)

    observer = Observer()
    observer.schedule(MyFileSystemEventHandler(send_message), real_path, recursive = False)
    observer.start()

    logging.info('Watching direction {}...'.format(real_path))
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()