#!/usr/bin/env python
"""
A very simple IRC bot that will join the servers and channels specified,
and then send out whatever is in the message queue, to the channels.

It can also parse input received from the channels, and execute commands
based on that.

"""
import socket
import threading
import Queue
import ssl
import logging

import messages
from constants import BASE_PATH
from ircparser import ircparser
from slight import slight


run = True


def dispatch_messages(sock, queue, channel):
    """Eat from the queue, and send messages to the IRC server."""
    while run:
        try:
            message = queue.get()
        except Queue.Empty:
            pass
        else:
            if message.recipient is None:
                message.recipient = channel
            sock.send("{0}\r\n".format(message.msg()))
            logging.debug("{0}".format(message.msg()))
            queue.task_done()

def handle_parsed(parsed, sock, queue, nick, channel, operator):
    """Act on the parsed IRC output."""
    if parsed.type == 'PING':
        sock.send('PONG :{0}\r\n'.format(parsed.msg))
    if parsed.type == 'PRIVMSG' and parsed.msg.startswith(operator):
        cmd = parsed.msg[1:].split()[0]
        args = ' '.join(parsed.msg[1:].split()[1:])
        if cmd == 'id':
            temp_msg = '{#type} {#recipient} :%s' % parsed.msg[4:]
            queue.put(messages.Message(temp_msg, recipient=channel))
        if cmd == 'build':
            if len(args.split('/')) == 2:
                owner, repo = args.split('/')
                slight.execute_shell_script({"name": owner, "repo_name": repo})
            else:
                temp_msg = '{#type} {#recipient} :Invalid argument! Usage: %sbuild Owner/Repo' % operator
                queue.put(messages.Message(temp_msg, recipient=channel))

def listen(sock, queue, nick, channel, operator):
    """Listen to the IRC output."""
    join_channel = True
    buff = ""
    while run:
        messages = sock.recv(4096).split("\r\n")
        for msg in messages[:-1]:
            if buff != "":
                msg = buff + msg
            parsed = ircparser.parse(msg, output='object')
            handle_parsed(parsed, sock, queue, nick, channel, operator)
            if join_channel:
                if "451" in msg or "NOTICE AUTH" in msg:
                    sock.send("NICK {0}\r\n".format(nick))
                    sock.send("USER slightCIb 0 * :slightCIb\r\n")
                    sock.send("JOIN :{0}\r\n".format(channel))
                if "JOIN :{0}".format(channel) in msg:
                    join_channel = False
        buff = messages[-1:][0]

def create_socket(addr, port, enable_ssl=False):
    """Create a socket, and wrap it in ssl if enabled."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if enable_ssl:
        sock = ssl.wrap_socket(sock)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(300)
    try:
        sock.connect((addr, port))
    except socket.gaierror: # Either wrong hostname or no connection.
        run = False
    except ssl.SSLError: # Problem has occured with SSL (check port)
        run = False
    else: # We have succesfully connected, so we can start parsing
        run = True
        return sock
    return None

def start_ircbot(server_list, operator):
    """Launchs threads for each IRC server."""
    logging.debug("Launching IRC bots")
    for name, server_info in server_list.items():
        server, nick, channel, port, ssl = (
            server_info['server'],
            server_info.get('nickname', 'slight-ci'), 
            server_info['channel'], 
            server_info['port'], 
            server_info.get('ssl', False)
        )
        sock = create_socket(server, port, ssl)
        if sock is not None:
            queue = messages.get_queue(sock)
            thread = threading.Thread(target=listen, args=(sock, queue, nick, channel, operator))
            thread.daemon = True
            thread.start()
            thread = threading.Thread(target=dispatch_messages, args=(sock, queue, channel))
            thread.daemon = True
            thread.start()
