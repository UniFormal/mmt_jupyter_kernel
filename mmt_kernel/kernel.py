import requests
import sys
from pexpect import replwrap

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from ipykernel.kernelbase import Kernel

MMT_SERVER_EXTENSION = 'repl'
MMT_BASE_URL = 'http://localhost:9000'


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
    STARTUP = True


    def __init__(self, **kwargs):
        super(MMTKernel,self).__init__(**kwargs)
        self.mmtsession = requests.Session()
        self.adapter = requests.adapters.HTTPAdapter()
        self.mmtsession.mount('https://', self.adapter)
        self.mmtsession.mount('http://', self.adapter)
        self.headers = {'content-type' : 'application/json',
                        'content-encoding' : 'UTF-8',
                        'mmtsession' : '12345xyz'}



    def do_execute(self, line, silent, store_history=True,user_expressions=None,allow_stdin=False):


        if(self.STARTUP):
            out = requests.get(MMT_BASE_URL + '/:' + MMT_SERVER_EXTENSION+'?start',data = None,headers = self.headers, stream = True)
            self.STARTUP = False

        binary_data = line.encode('UTF-8')

        stream_content = {
            'data': {
                'text/html':  self.mmtsession.post(MMT_BASE_URL + '/:' + MMT_SERVER_EXTENSION,data = binary_data,headers = self.headers, stream = True).text
            },
            'metadata': {},
            'transient': {},
        }

        if not silent:
            res = self.send_response(self.iopub_socket, 'display_data',stream_content)

            return {'status': 'ok',
            # The base class increments the execution count
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
            }
