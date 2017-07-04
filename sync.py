#!/usr/bin/env python

import time
import threading
import paramiko
import common
import logging

class Sync:
    _queue = []
    _closed = False
    _lock = threading.Lock()

    def sync_thread(self):
        while not self._closed:
            if self.count() > 0:
                with self._lock:
                    filename = self._queue.pop()
                try:
                    self.sync_file(filename)
                except Exception as e:
                    logging.error(e)
            else:
                time.sleep(1)

    def sync_file(self, filename):
        logging.info('start sync file:{}'.format(filename))

        localFile = '{}/{}'.format(common.voice_path, filename)
        remoteFile = '{}/{}'.format(common.ssh_path, filename)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        client.connect(common.ssh_server, common.ssh_port, common.ssh_username, common.ssh_password)

        sftp = client.open_sftp()
        sftp.put(localFile, remoteFile)
        sftp.close()
        client.close()

        logging.info('end sync file:{}'.format(filename))

    def count(self):
        return len(self._queue)

    def enter(self, name):
        with self._lock:
            self._queue.append(name)
        if self._closed:
            self._closed = False
            thread = threading.Thread(target= self.sync_thread)
            thread.start()


    def close(self):
        self._closed = True

    def __init__(self):
        thread = threading.Thread(target=self.sync_thread)
        thread.start()
