# URL Shortener
#
# This script is a plugin for WeeChat 1.0.1 that helps you shortening your URLs,
# wether you want them replaced in outgoing/incoming messages or shortened under
# the incoming messages.
#
# Copyright (c) 2015 by Nicolas Jeannerod - Niols <niols@niols.net>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import re
import weechat
from urllib import quote_plus, urlencode
from urllib2 import urlopen

SCRIPT_NAME = "urlshortener"
SCRIPT_AUTHOR = "Niols <niols@niols.net>"
SCRIPT_VERSION = "0.2"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESCRIPTION = ("Helps you shortening your URLs, wether you want them" +
                      "replaced in outgoing/incoming messages or shortened " +
                      "under the incoming messages.")

settings = {
    'add_under.status': 'on',
    'add_under.color': 'darkgray',
    'add_under.prefix': '> ',
    'add_under.suffix': '',

    'replace_in.status': 'off',

    'replace_out.status': 'off',

    'length': '45',
    'shortener': 'http://is.gd/create.php?format=simple&url=%s',
    'shortener_method': 'get'
}


# Create URL regexp.
ur_octet = r'(?:2(?:[0-4]\d|5[0-5])|1\d\d|\d{1,2})'
ur_ip_addr = r'%s(?:\.%s){3}' % (ur_octet, ur_octet)
ur_label = r'[0-9a-z][-0-9a-z]*[0-9a-z]?'
ur_domain = r'%s(?:\.%s)*\.[a-z][-0-9a-z]*[a-z]?' % (ur_label, ur_label)
url_regexp = re.compile(
    r'(http[s]?://(?:%s|%s)(?::\d+)?(?:/[^\])>\s]*)?)' %
    (ur_domain, ur_ip_addr),
    re.I
)


# Register WeeChat plugin, add options to WeeChat and add hooks.
if weechat.register(SCRIPT_NAME,
                    SCRIPT_AUTHOR,
                    SCRIPT_VERSION,
                    SCRIPT_LICENSE,
                    SCRIPT_DESCRIPTION, "", ""):
    for option, default_value in settings.iteritems():
        if weechat.config_get_plugin(option) == '':
            weechat.config_set_plugin(option, default_value)

    weechat.hook_print('', 'irc_privmsg', '', 1, 'privmsg', '')
    weechat.hook_modifier('irc_in_privmsg', 'in_privmsg', '')
    weechat.hook_modifier('irc_out1_privmsg', 'out_privmsg', '')


# For every message, if it's not your message, and if the `add_under` section
# is activated, prints every shortened URL in the specified color with the
# specified prefix and suffix under the message.
def privmsg(data, buf, date, tags, displayed, hilight, prefix, msg):
    if prefix == weechat.buffer_get_string(buf, 'localvar_nick'):
        return weechat.WEECHAT_RC_OK

    if weechat.config_get_plugin('add_under.status') == 'off':
        return weechat.WEECHAT_RC_OK

    color = weechat.color(weechat.config_get_plugin('add_under.color'))
    reset = weechat.color('reset')
    prefix = weechat.config_get_plugin('add_under.prefix')
    suffix = weechat.config_get_plugin('add_under.suffix')

    for url in get_urls_to_shorten(msg):
        new_url = shorten_url(url)
        if new_url != url:
            weechat.prnt(buf,
                         '%(color)s%(prefix)s%(url)s%(suffix)s%(reset)s' %
                         {'color': color, 'reset': reset,
                          'prefix': prefix, 'suffix': suffix,
                          'url': shorten_url(url)})

    return weechat.WEECHAT_RC_OK


# For every incoming message, if the `replace_in` section is activated,
# replaces all URLs by their shortened version.
def in_privmsg(data, modifier, modifier_data, msg):
    if weechat.config_get_plugin('replace_in.status') == 'off':
        return msg

    for url in get_urls_to_shorten(msg):
        new_url = shorten_url(url)
        if new_url != url:
            msg = msg.replace(url, new_url)

    return msg


# For every outgoing message, if the `replace_out` section is activated,
# replaces all URLs by their shortened version.
def out_privmsg(data, modifier, modifier_data, msg):
    if weechat.config_get_plugin('replace_out.status') == 'off':
        return msg

    for url in get_urls_to_shorten(msg):
        msg = msg.replace(url, shorten_url(url))

    return msg


# Returns all URLs found in a string if their length is over the `length`
# parameter.
def get_urls_to_shorten(msg):
    max_url_length = int(weechat.config_get_plugin('length'))
    return [url
            for url in url_regexp.findall(msg)
            if len(url) > max_url_length]


# Returns the shortened version of an URL if it can, and the URL otherwise.
def shorten_url(url):
    try:
        shortener_url = weechat.config_get_plugin('shortener')
        if weechat.config_get_plugin('shortener_type') == 'post':
            data = urlencode({"url": url})
            new_url = urlopen(shortener_url, data=data).read()
        else:
            # GET method is the default one
            shortener_url = shortener_url % quote_plus(url)
            new_url = urlopen(shortener_url).read()

        if url_regexp.match(new_url) and len(new_url) < len(url):
            return new_url
        else:
            return url
    except:
        pass

    return url
