import weechat
from urllib import quote

weechat.register('lmddgtfy', 'Niols', '1.0', 'GPL3', 'Provides the /lmddgtfy command.', '', '')

def lmddgtfy_cmd(data, buffer, args):
	weechat.command(buffer, 'https://lmddgtfy.net/?q=%s'%(quote(args),))
	return weechat.WEECHAT_RC_OK

hook = weechat.hook_command('lmddgtfy', 'Returns the url of lmddgtfy for the search string you entered', 'search string', '', '', 'lmddgtfy_cmd', '')
