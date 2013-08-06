import socket
import threading
import Queue
import ssl

from ircparser import ircparser
from slight import DEBUG


run = True
queue_holder = {}

def add_to_queue(msg):
    for sock, queue in queue_holder.items():
        queue.put(msg)

def eat_queue(sock, queue, channel):
    while run:
        try:
            send_msg = queue.get()
        except Queue.Empty:
            pass
        else:
            sock.send("PRIVMSG {0} :{1}\r\n".format(channel, send_msg))
            if DEBUG: print "@@@ PRIVMSG {0} :{1}".format(channel, send_msg)
            queue.task_done()

def parse(parsed, sock, queue, nick, channel):
    if parsed.type == 'PING':
        sock.send('PONG :{0}\r\n'.format(parsed.msg))
    if parsed.type == 'PRIVMSG':
        if parsed.msg.startswith('!id '):
            add_to_queue(parsed.msg[5:])

def listen(sock, queue, nick, channel):
    join_channel = True
    buff = ""
    while run:
        messages = sock.recv(4096).split("\r\n")
        for msg in messages[:-1]:
            if buff != "":
                msg = buff + msg
            parsed = ircparser.parse(msg, output='object')
            parse(parsed, sock, queue, nick, channel)
            if join_channel:
                if "451" in msg or "NOTICE AUTH" in msg:
                    sock.send("NICK {0}\r\n".format(nick))
                    sock.send("USER slightCIb 0 * :slightCIb\r\n")
                    sock.send("JOIN :{0}\r\n".format(channel))
                if "JOIN :{0}".format(channel) in msg:
                    join_channel = False
        buff = messages[-1:][0]

def create_socket(addr, port, enable_ssl=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if enable_ssl:
        sock = ssl.wrap_socket(sock)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(300)
    try:
        sock.connect((addr, port))
    except socket.gaierror: # Either wrong hostname or no connection. Trying again.
        run = False
    except ssl.SSLError: # Problem has occured with SSL (check you're using the right port)
        run = False
    else: # We have succesfully connected, so we can start parsing
        return sock
    return None

def start_ircbot(server_list):
    for server, info in server_list.items():
        nick, channel, port, ssl = (info['nickname'], info['channel'], info['port'], info['ssl'])
        sock = create_socket(server, port, ssl)
        if sock is not None:
            queue_holder[sock] = Queue.Queue()
            queue = queue_holder[sock]
            t = threading.Thread(target=listen, args=(sock, queue, nick, channel))
            t.start()
            t = threading.Thread(target=eat_queue, args=(sock, queue, channel))
            t.start()
