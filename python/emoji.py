# coding: utf-8
#FIXME

SCRIPT_NAME    = 'emoji'
SCRIPT_AUTHOR  = 'Niols <niols@niols.fr>'
SCRIPT_VERSION = '0.2'
SCRIPT_LICENSE = 'WTFPL'
SCRIPT_DESC    = 'FIXME'

try:
    import weechat
except Exception:
    print('This script must be run under Weechat.')
    print('Get it now at: <http://www.weechat.org/>')
    quit()

import requests

################################ [ Parameters ] ################################

headers = {
    'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'
}

################################# [ Helpers ] ##################################

cache = {}

def add_to_cache(emoji, name):
    cache[emoji] = name

def get_name_from_cache(emoji):
    if emoji in cache:
        return cache[emoji]
    else:
        return None

def get_emoji_from_cache(name):
    for emoji in cache:
        if cache[emoji] == name:
            return emoji
    return None

def emoji_to_name(emoji):
    name = get_name_from_cache(emoji)
    if name != None:
        return name
    r = requests.get (
        'https://emojipedia.org/%s/' % emoji.encode('utf-8'),
        headers = headers,
        allow_redirects = False
    )
    if not r.status_code == 301:
        raise FIXME
    name = r.headers['Location'].split('/')[-2]
    add_to_cache(emoji, name)
    return name

def emoji_from_name(name):
    if name == '':
        return None
    for char in name:
        if char not in 'abcdefghijklmnopqrstuvwxyz-':
            return None
    emoji = get_emoji_from_cache(name)
    if emoji != None:
        return emoji
    r = requests.get (
        'https://emojipedia.org/%s/' % name,
        headers = headers
    )
    if r.status_code == 404:
        return None
    title_start = r.text.index('<title>') + 7
    emoji = r.text[title_start]
    return emoji

def emoji_to_name_in_string(string):
    string = string.decode('utf-8')
    output = ''
    for char in string:
        output += ':'+emoji_to_name(char)+':' if ord(char) > 10000 else char.encode('utf-8')
    return output

def emoji_from_name_in_string(string):
    string = string.split(':')
    output = ''
    prev_colon = False
    for part in string:
        if prev_colon:
            new_part = emoji_from_name(part)
            if new_part != None:
                output += new_part.encode('utf-8')
                prev_colon = False
            else:
                output += ':'+part
                prev_colon = True
        else:
            output += part
            prev_colon = True
    return output

################################ [ Callbacks ] #################################

def irc_in_privmsg(data, modifier, modifier_data, message):
    [before, content] = message.split(' :', 1)
    content = emoji_to_name_in_string(content)
    return before + ' :' + content

def irc_out1_privmsg(data, modifier, modifier_data, message):
    [before, content] = message.split(' :', 1)
    content = emoji_from_name_in_string(content)
    return before + ' :' + content

def weechat_print(data, modifier, modifier_data, message):
    message = emoji_to_name_in_string(message)
    return message

################################### [ Main ] ###################################

if __name__ == '__main__':
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
                        SCRIPT_LICENSE, SCRIPT_DESC, '', ''):
        weechat.hook_modifier('irc_in_privmsg', 'irc_in_privmsg', '')
        weechat.hook_modifier('irc_out1_privmsg', 'irc_out1_privmsg', '')
        weechat.hook_modifier('weechat_print', 'weechat_print', '')
