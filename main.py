#!/usr/bin/env python
"""
Launch the slight server, and IRC bot.

"""
import sys
import os
import threading
import logging

from constants import BASE_PATH
from daemon import Daemon
import slight.settings as settings
from slight.slight import run_server
from irc import ircbot


PIDFILE = BASE_PATH + "/slight-ci.pid"


def main():
    if settings.create_first():
        print "A settings file has been created at `settings.yaml`"
        sys.exit(0)
    check_settings = settings.check_validity()
    if check_settings is False:
        print "\nPlease fix your settings file!"
        sys.exit(0)
    try:
        if check_settings is not None:
            irc = settings.get_irc_settings()
            operator = irc.get('operator', '!')
            if irc.get('enabled', False):
                del irc['operator']
                del irc['enabled']
                ircbot.start_ircbot(irc, operator)
        run_server()
    except KeyboardInterrupt:
        ircbot.run = False
        sys.exit(0)
    except Exception, excep:
        exception = str(excep)
        logging.exception("Uncaught Exception")

class MyDaemon(Daemon):
        def run(self):
            main()
 
if __name__ == "__main__":
    FORMAT = "%(levelname)-5s %(asctime)s %(funcName)-25s %(lineno)-4d :: %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    logging.disable(logging.CRITICAL)
    daemon = MyDaemon(PIDFILE)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.status()
        elif 'run' == sys.argv[1]:
            logging.disable(logging.NOTSET)
            daemon.run()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart|status|run" % sys.argv[0]
        sys.exit(2)
