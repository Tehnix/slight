#!/usr/bin/env python
"""
Launch the slight server, and IRC bot.

"""
import sys
import threading

import slight.settings as settings
from slight.slight import run_server
from irc import ircbot

if __name__ == "__main__":
    if settings.create_first():
        print "A settings file has been created at `slight.yaml`"
        sys.exit(0)
    check_settings = settings.check_validity()
    if check_settings and check_settings is not None:
        servers = settings.fetch_irc_servers()
        ircbot.start_ircbot(servers)
    if check_settings or check_settings is None:
        thread = threading.Thread(target=run_server)
        thread.start()
        thread.join()