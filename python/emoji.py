# coding: utf-8
#FIXME

SCRIPT_NAME    = 'emoji'
SCRIPT_AUTHOR  = 'Niols <niols@niols.fr>'
SCRIPT_VERSION = '0.1'
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
    return None #FIXME

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

################################ [ Callbacks ] #################################

def irc_in_privmsg(data, modifier, modifier_data, message):

    [before, content] = message.split(' :', 1)
    content = content.decode('utf-8')
    new_content = ''

    for char in content:
        new_content += ':'+emoji_to_name(char)+':' if ord(char) > 10000 else char.encode('utf-8')

    new_message = before + ' :' + new_content
    return new_message

################################### [ Main ] ###################################

if __name__ == '__main__':
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
                        SCRIPT_LICENSE, SCRIPT_DESC, '', ''):
        weechat.hook_modifier('irc_in_privmsg', 'irc_in_privmsg', '')
        #FIXME: out
