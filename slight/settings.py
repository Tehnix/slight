#!/usr/bin/env python
"""
Handle the settings file. Initial creation, validation, etc.

"""
import os
import yaml

from constants import BASE_PATH

SETTINGS_FILE = BASE_PATH + "/settings.yaml"
settings = None


def create_first():
    """Create a slight.yaml settings file if none exists."""
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'w') as conf:
            conf.write("\n".join([
                "# -- Example usage of irc --",
                "#irc:",
                "#    irc.freenode.net:",
                "#        port: 6697",
                "#        ssl: true",
                "#        channel: \"#lobby\"",
                "#        nickname: \"slight-ci\"",
                "notifications:",
                "    jobs: \"privmsg\"",
                "    issues: \"notice\"",
                "    commands: \"notice\""
            ]))
        return True
    return False

def check_validity():
    """Check if the settings file is valid."""
    with open(SETTINGS_FILE, 'r') as conf:
        settings = yaml.safe_load(conf)
        irc = settings.get('irc')
        del irc['operator']
        del irc['enabled']
        if settings is not None and irc is not None:
            for _, info in irc.items():
                if (info.get('port') is None
                   or info.get('channel') is None 
                   or info.get('server') is None):
                    print ''.join([
                        "Invalid slight.conf file. server, ",
                        "port and channel must be set!"
                    ])
                    return False
            return True
    return None

def get_settings():
    global settings
    if settings is not None:
        return settings
    with open(SETTINGS_FILE, 'r') as conf:
        loaded_settings = yaml.safe_load(conf)
        settings = loaded_settings
        return loaded_settings
    return None

def get_irc_settings():
    """Extract the IRC servers from the settings file."""
    return get_settings().get('irc')

def get_notifications_settings():
    """Get notification settings from the settings file."""
    notif = get_settings().get('notifications')
    if notif is not None:
        jobs = notif.get('jobs', 'PRIVMSG').upper()
        issues = notif.get('issues', 'NOTICE').upper()
        commands = notif.get('commands', 'NOTICE').upper()
        if jobs != 'NOTICE' or jobs != 'PRIVMSG':
            jobs = 'PRIVMSG'
        if issues != 'NOTICE' or issues != 'PRIVMSG':
            issues = 'NOTICE'
        if commands != 'NOTICE' or commands != 'PRIVMSG':
            commands = 'NOTICE'
    
