WeeChat Scripts
===============

This repo contains some WeeChat scripts. Some of them might even be usefull!



### How can I use the script `brouillamini.py`?

1. Copy this script in your WeeChat python directory: `~/.weechat/python/brouillamini.py`.
2. Copy the `data/brouillamini/` directory in `~/.weechat/python/data/brouillamini/` if such a repository exists on the server.
3. Load the plugin in WeeChat: `/python load brouillamini.py` (don't forget the `.py`)
4. If you want the script to be automatically loaded each time WeeChat starts, link it in the autoload directory: `cd ~/.weechat/python/ && ln -s brouillamini.py autoload/`

If you're lazy, you can do that with all scripts at the same time:

    weepydir=~/.weechat/python
    mkdir -p $weepydir
    git clone https://github.com/Niols/WeeChat-Scripts /tmp/wcs
    cp -r .tmp/wcs/*.py /tmp/wcs/data/ $weepydir/
    mkdir -p $weepydir/autoload
    ln -s $weepydir/*.py $weepydir/autoload/



### Why the GPLv3 license?

Because the [Python Plugin](https://github.com/weechat/weechat/tree/master/src/plugins/python) for WeeChat is licensed under the GPLv3.
