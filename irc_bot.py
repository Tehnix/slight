import socket
import threading
import Queue
import ssl

from slight import DEBUG


run = True
queue_holder = {}

def add_to_queue(msg):
    for sock, queue in queue_holder.items():
        queue.put(msg)

def start_irc_bot(server_list):
    for server, info in server_list.items():
        nick, channel, port, ssl = (info['nickname'], info['channel'], info['port'], info['ssl'])
        sock = create_socket(server, port, ssl)
        if sock is not None:
            queue_holder[sock] = Queue.Queue()
            queue = queue_holder[sock]
            t = threading.Thread(target=run_forever, args=(sock, nick, channel, queue))
            t.start()

def create_socket(addr, port, enable_ssl=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if enable_ssl:
        sock = ssl.wrap_socket(sock)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(300)
    try:
        sock.connect((addr, port))
    except socket.gaierror: # Either wrong hostname or no connection. Trying again.
        #time.sleep(60)
        pass
    except ssl.SSLError: # Problem has occured with SSL (check you're using the right port)
        pass
    else: # We have succesfully connected, so we can start parsing
        return sock
    return None

def run_forever(sock, nick, channel, queue):
    join_channel = True
    buff = ""
    while run:
        try:
            send_msg = queue.get_nowait()
            sock.send("PRIVMSG {0} :{1}\r\n".format(channel, send_msg))
            if DEBUG: print "@@@ PRIVMSG {0} :{1}".format(channel, send_msg)
        except Queue.Empty:
            messages = sock.recv(4096).split("\r\n")
            for msg in messages[:-1]:
                if buff != "":
                    msg = buff + msg
                if msg.startswith('PING'):
                    pong = msg.split(':')[1]
                    sock.send('PONG :{0}\r\n'.format(pong))
                if join_channel:
                    if "451" in msg or "NOTICE AUTH" in msg:
                        register(sock, nick, channel)
                parse(sock, msg)
            buff = messages[-1:][0]

def register(sock, nick, channel):
    sock.send("NICK {0}\r\n".format(nick))
    sock.send("USER slightCIb 0 * :slightCIb\r\n")
    sock.send("JOIN :{0}\r\n".format(channel))

def parse(sock, msg):
    # print msg
    pass
