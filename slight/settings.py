#!/usr/bin/env python
"""
Handle the settings file. Initial creation, validation, etc.

"""
import os
import yaml


DEBUG = False


def create_first():
    """Create a slight.yaml settings file if none exists."""
    if not os.path.exists('slight.yaml'):
        with open('slight.yaml', 'w') as conf:
            conf.write("\n".join([
                "# -- Example of usage --",
                "#irc:",
                "#    irc.freenode.net:",
                "#        port: 6697",
                "#        ssl: true",
                "#        channel: \"#lobby\"",
                "#        nickname: \"slight-ci\""
            ]))
        return True
    return False

def check_validity():
    """Check if the settings file is valid."""
    with open('slight.yaml', 'r') as conf:
        settings = yaml.safe_load(conf)
        irc = settings.get('irc')
        if settings is not None and irc is not None:
            for _, info in irc.items():
                if (info.get('port') is None or info.get('ssl') is None
                   or info.get('channel') is None 
                   or info.get('nickname') is None):
                    print ''.join([
                        "Invalid slight.conf file. nickname, ",
                        "port, ssl and channel must be set!"
                    ])
                    return False
                return True
    return None

def fetch_irc_servers():
    """Extract the IRC servers from the settings file."""
    with open('slight.yaml', 'r') as conf:
        settings = yaml.safe_load(conf)
        return settings.get('irc')
