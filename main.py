#!/usr/bin/env python
"""
Launch the slight server, and IRC bot.

"""
import sys
import threading

DEBUG = False

from slight.slight import *

if __name__ == "__main__":
    if create_first_settings_file():
        print "A settings file has been created at `slight.yaml`"
        sys.exit(0)
    check_settings = check_settings_validity()
    if check_settings and check_settings is not None:
        servers = fetch_irc_servers_from_settings()
        ircbot.start_ircbot(servers)
    if check_settings or check_settings is None:
        t = threading.Thread(target=run_server)
        t.start()
        t.join()