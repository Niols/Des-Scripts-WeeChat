import weechat


################################################################################
# This scripts integrates the latex-to-unicode work from ypsu into Weechat
# Here begins the convert.py file convert.py
# https://github.com/ypsu/latex-to-unicode
# I just changed the data directory in load_*
#

import re
from os.path import expanduser # Niols-added

def convert(s):
	global data_loaded

	if data_loaded == False:
		load_data()
		data_loaded = True

	ss = convert_single_symbol(s)
	if ss != None:
		return ss

	s = convert_latex_symbols(s)
	s = process_starting_modifiers(s)
	s = apply_all_modifiers(s)
	return s

# If s is just a latex code "alpha" or "beta" it converts it to its
# unicode representation.
def convert_single_symbol(s):
	ss = "\\" + s
	for (code, val) in latex_symbols:
		if code == ss:
			return val
	return None

# Replace each "\alpha", "\beta" and similar latex symbols with
# their unicode representation.
def convert_latex_symbols(s):
	for (code, val) in latex_symbols:
		s = s.replace(code, val)
	return s

# If s start with "it ", "cal ", etc. then make the whole string
# italic, calligraphic, etc.
def process_starting_modifiers(s):
	s = re.sub("^bb ", r"\\bb{", s)
	s = re.sub("^bf ", r"\\bf{", s)
	s = re.sub("^it ", r"\\it{", s)
	s = re.sub("^cal ", r"\\cal{", s)
	s = re.sub("^frak ", r"\\frak{", s)
	s = re.sub("^mono ", r"\\mono{", s)
	return s

def apply_all_modifiers(s):
	s = apply_modifier(s, "^", superscripts)
	s = apply_modifier(s, "_", subscripts)
	s = apply_modifier(s, "\\bb", textbb)
	s = apply_modifier(s, "\\bf", textbf)
	s = apply_modifier(s, "\\it", textit)
	s = apply_modifier(s, "\\cal", textcal)
	s = apply_modifier(s, "\\frak", textfrak)
	s = apply_modifier(s, "\\mono", textmono)
	return s

# Example: modifier = "^", D = superscripts
# This will search for the ^ signs and replace the next
# digit or (digits when {} is used) with its/their uppercase representation.
def apply_modifier(text, modifier, D):
	text = text.replace(modifier, "^")
	newtext = ""
	mode_normal, mode_modified, mode_long = range(3)
	mode = mode_normal
	for ch in text:
		if mode == mode_normal and ch == '^':
			mode = mode_modified
			continue
		elif mode == mode_modified and ch == '{':
			mode = mode_long
			continue
		elif mode == mode_modified:
			newtext += D.get(ch, ch)
			mode = mode_normal
			continue
		elif mode == mode_long and ch == '}':
			mode = mode_normal
			continue

		if mode == mode_normal:
			newtext += ch
		else:
			newtext += D.get(ch, ch)
	return newtext

def load_data():
	load_symbols()
	load_dict("subscripts", subscripts) # Niols-modified
	load_dict("superscripts", superscripts) # Niols-modified
	load_dict("textbb", textbb) # Niols-modified
	load_dict("textbf", textbf) # Niols-modified
	load_dict("textit", textit) # Niols-modified
	load_dict("textcal", textcal) # Niols-modified
	load_dict("textfrak", textfrak) # Niols-modified
	load_dict("textmono", textmono) # Niols-modified

def load_dict(filename, D):
	with open( weechat.info_get('weechat_dir', '') + '/python/data/latex/' + filename, 'r') as f: # Niols-modified
		line = f.readline()
		while line != "":
			words = line.split()
			code = words[0]
			val = words[1]
			D[code] = val
			line = f.readline()

def load_symbols():
	with open( weechat.info_get('weechat_dir', '') + '/python/data/latex/symbols', 'r') as f: # Niols-modified
		line = f.readline()
		while line != '':
			words = line.split()
			code = words[0]
			val = words[1]
			latex_symbols.append((code, val))
			line = f.readline()


data_loaded = False

superscripts = {}
subscripts = {}
textbb = {}
textbf = {}
textit = {}
textcal = {}
textfrak = {}
textmono = {}
latex_symbols = []

#
# Here ends the convert.py file
################################################################################


weechat.register('LaTeX', 'Nicolas Jeannerod', '1.0', 'GPL3', 'Provides the /latex command, to include LaTeX text in Weechat.', '', '')

def latex_cmd(data, buffer, args):
	weechat.command(buffer, convert(args))
	return weechat.WEECHAT_RC_OK

hook = weechat.hook_command('latex', 'The /latex command tries to convert in unicode the given LaTeX symbols.', 'LaTeX code', '', '', 'latex_cmd', '')
