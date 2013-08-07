"""
Handle the queue for messages, and the message object.

"""
import Queue
import logging

from constants import BASE_PATH


queue_holder = {}


class Message(object):
    """Handle messages."""
    
    def __init__(self, msg, recipient=None, kind="PRIVMSG", raw=False):
        """Initialize the object."""
        super(Message, self).__init__()
        self._msg = msg
        self.raw = raw
        self.kind = kind
        self.recipient = recipient
    
    def msg(self, recipient=None, kind=None):
        """Perform replacement on template names."""
        if kind is not None:
            self.kind = kind
        if recipient is not None:
            self.recipient = recipient
        msg = self._msg
        if not self.raw:
            msg = self._msg\
                .replace('{#recipient}', self.recipient)\
                .replace('{#type}', self.kind)
        return msg

def notify(msg, queue=None, custom=False):
    """Add the message to the ircbot queue."""
    logging.debug(msg)
    if not custom:
        logging.info("Adding type and recipient template to msg...".format(msg))
        msg = '{#type} {#recipient} :%s' % msg
    msg = Message(msg)
    if queue is not None:
        queue.put(msg)
    else:
        add_to_queue(msg)

def get_queue(sock):
    """Returns a Queue object, associated to the socket."""
    if sock not in queue_holder:
        queue_holder[sock] = Queue.Queue()
    return queue_holder[sock]

def add_to_queue(msg):
    """Add a message to all IRC server queues."""
    for _, queue in queue_holder.items():
        queue.put(msg)
