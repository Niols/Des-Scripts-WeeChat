#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import weechat
from sys import argv
from string import ascii_letters
from unicodedata import normalize

weechat.register('asciiwrite', 'Niols', '1.0', 'GPL3', 'Tu veux spam des chans en énorme ? Ce script est fait pour toi !', '', '')

def get_char (c):
    try:
        with open( weechat.info_get('weechat_dir', '') + '/python/data/asciiwrite/font/' + str(ord(c)), 'r' ) as f:
            return f.read().split('\n')
    except:
        weechat.prnt('', 'Did not found char %s [%d]. Replacing by NULL.' % (c, ord(c)))
        return []

def asciiwrite_cmd (data, buffer, args):

    # On récupère les caractères
    args = [get_char(c) for c in args]

    height = 0
    for char in args:
        if len(char) > height:
            height = len(char)

    args = [ char + ['']*(height-len(char)) for char in args ]

    new_args = []
    for char in args:
        width = 0
        for line in char:
            if len(line) > width:
                width = len(line)
        new_args.append([ line + ' '*(width-len(line)) for line in char ])
    args = new_args

    ascii = [''] * len(args[0])

    for char in args:
        for i in range(len(char)):
            ascii[i] += char[i]

    for line in ascii:
        if line[0] == '/':
            line = '/'+line
        weechat.command (buffer, line)
    weechat.command (buffer, ' ')
    return weechat.WEECHAT_RC_OK

hook = weechat.hook_command('asciiwrite', 'The /asciiwrite command converts the given text into ascii art line.', 'string to transform', '', '', 'asciiwrite_cmd', '')
