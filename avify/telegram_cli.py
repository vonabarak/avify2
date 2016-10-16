# -*- coding: utf-8 -*-
import subprocess
import shlex
import socket

settings = {
    'user': 'telegram',
    'path': '/bin/telegram-cli',
    'host': 'localhost',
    'port': 4457,
}

class Messenger:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.subproc = subprocess.Popen(shlex.split(
            'sudo -u {user} {path} -W --json -P{port}'.format(
                user=settings['user'],
                port=settings['port'],
                path=settings['path']
            )
        ), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def connect(self):
        self.socket.connect((settings['host'], settings['port']))

    def command(self, command):
        self.socket.send(command+'\n')
        size_str = str()
        size = 0
        answer = self.socket.recv(7)
        if answer != 'ANSWER ':
            print('something wrong!')
        while True:
            i = self.socket.recv(1)
            if i != '\n':
                size_str = size_str + i
            else:
                size = int(size_str)
                size_str = ''
                break
        return self.socket.recv(size)
