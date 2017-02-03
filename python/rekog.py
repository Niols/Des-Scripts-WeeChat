# coding: utf-8
#
# Copyright (c) 2017 by Niols <niols@niols.fr>
#
# Recognizes URLs in incoming messages, compare the image they point
# to to a database, and replace them by an other string if needed.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Development is currently hosted at
# <https://github.com/Niols/weechat-scripts>.

try:
    import weechat
except Exception:
    print('This script must be run under Weechat.')
    print('Get Weechat now at: <http://www.weechat.org/>')
    quit()

from sys import version_info

if version_info.major == 2:
    from urllib2 import urlopen
    from cStringIO import StringIO as BytesIO
else:
    from urllib.request import urlopen
    from io import BytesIO

try:
    from PIL import Image
except Exception: 
    weechat.prnt('', 'This script requires PIL in order to work.')
    weechat.prnt('', 'Get it now at: <http://python-pillow.org/>.')
    
from re import compile as compile_regex
from re import IGNORECASE
from os.path import join as join_path
from math import sqrt
from traceback import format_exc

SCRIPT_NAME    = 'rekog'
SCRIPT_AUTHOR  = 'Niols <niols@niols.fr>'
SCRIPT_VERSION = '0.2'
SCRIPT_LICENSE = 'GPL'
SCRIPT_DESC    = 'Recognizes URLs in incoming messages, compare the image they point to to a database, and replace them by an other string if needed.'


# =============================== [ helpers ] ================================ #

def get_full_path(path):
    return join_path(weechat.info_get('weechat_dir', ''), 'python',
                     SCRIPT_NAME, path)

# ============================== [ URL regex ] =============================== #

url_octet = r'(?:2(?:[0-4]\d|5[0-5])|1\d\d|\d{1,2})'
url_ip_addr = r'%s(?:\.%s){3}' % (url_octet, url_octet)
url_label = r'[0-9a-z][-0-9a-z]*[0-9a-z]?'
url_domain = r'%s(?:\.%s)*\.[a-z][-0-9a-z]*[a-z]?' % (url_label, url_label)
url_regex = compile_regex(
    r'(http[s]?://(?:%s|%s)(?::\d+)?(?:/[^\])>\s]*)?)' % (url_domain, url_ip_addr),
    IGNORECASE
)

# ========================== [ images comparison ] =========================== #

def fast_normalize (im1, im2):
    # Makes sure that the two images have the same size. This function
    # does not care about proportions.
    
    (x1, y1) = im1.size
    (x2, y2) = im2.size

    if x1 * y1 > x2 * y2:
        return fast_normalize (im2, im1)

    else:
        return (im1, im2.resize((x1, y1)))

def fast_compare (im1, im2, threshold = 0):
    # Compares two images in a really fast way. This isn't very
    # accurate, but that's enough for our use case.
    
    (im1, im2) = fast_normalize (im1, im2)

    try:
        h1 = im1.histogram()
        h2 = im2.histogram()
    except IndexError:
        return False

    diff_squares = [(h1[i] - h2[i]) ** 2 for i in range(min(len(h1),len(h2)))]
    rms = sqrt(sum(diff_squares) / len(h1))

    weechat.prnt('', '%s: Matched with a RMS of %s.' % (SCRIPT_NAME, str(rms)))
    
    return (rms <= threshold)

# ============================= [ replacement ] ============================== #

replacement_database = [
    ('facebook_thumbsup', 'facebook_thumbsup.png', ':thumbsup:', 10)
]

def find_replacement (url):
    try:
        im = Image.open(BytesIO(urlopen(url).read()))
    except IOError:
        return None

    for (name, path, replacement, threshold) in replacement_database:
        if fast_compare (Image.open(get_full_path(path)), im, threshold):
            return replacement

    return None

# ============================== [ callbacks ] =============================== #

def cb_in_privmsg(data, modifier, modifier_data, message):
    # This is the callback called at each incoming PRIVMSG. It must
    # return a valid IRC command (and, in our case, a valid PRIVMSG).
    
    try:
        for url in url_regex.findall(message):
            replacement = find_replacement(url)
            if replacement:
                message = message.replace(url, replacement)
                
    except:
        for line in format_exc().split('\n'):
            if line:
                weechat.prnt('', '%s: %s' % (SCRIPT_NAME, line))
        
    return message

# ================================= [ main ] ================================= #

if __name__ == '__main__':
    
    # We first register our plugin into Weechat.
    if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
                        SCRIPT_LICENSE, SCRIPT_DESC, '', ''):

        # If that works, we add our hook for incoming messages
        weechat.hook_modifier('irc_in_privmsg', 'cb_in_privmsg', '')
