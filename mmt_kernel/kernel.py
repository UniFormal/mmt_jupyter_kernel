import requests
from . import mmtshell
import sys
from pexpect import replwrap

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from ipykernel.kernelbase import Kernel



class MMTKernel(Kernel):
    implementation = 'MMT'
    implementation_version = '1.2'
    language = 'mmt-action-script'
    language_version = '0.1'
    language_info = {
        'name': 'Any text',
        'mimetype': 'text/plain',
        'file_extension': '.txt',
    }
    banner = "MMT kernel - running build command on MMT"

    def do_execute(self, line, silent, store_history=True,
                   user_expressions=None,
                   allow_stdin=False):
       if not silent:
           stream_content = s.handleInputFromKernel(line)
           res = self.send_response(self.iopub_socket, 'display_data',
           stream_content)

           return {'status': 'ok',
               # The base class increments the execution count
               'execution_count': self.execution_count,
               'payload': [],
               'user_expressions': {},
           }

s = mmtshell.MMTShell()
