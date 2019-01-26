import socket
from contextlib import closing

def check_port(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            res = True
        else:
            res = False
    return res

def generate_port(h="localhost", start=20000, end=30000):
    for p in range(start, end):
        if not check_port(h, p):
            return p

def to_display_data(message,omdoc=None):
    """wraps the message into the display_data format"""
    if(omdoc):
        return {
            'data': {
                'text/html': message,
                'application/omdoc' : omdoc
            },
            'metadata': {},
            'transient': {},
        }
    else:
        return {
            'data': {
                'text/html': message,
            },
            'metadata': {},
            'transient': {}
        }
