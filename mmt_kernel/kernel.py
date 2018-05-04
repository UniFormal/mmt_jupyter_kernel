import requests
import sys
import os
import json
from pexpect import replwrap

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from ipykernel.kernelbase import Kernel

MMT_SERVER_EXTENSION = 'repl'
MMT_BASE_URL = os.environ.setdefault('MMT_BASE_URL', 'http://localhost:9000')


class MMTError(Exception):
    message = ''
    def __init__(self,message,**kwargs):
        Exception.__init__(self,message,**kwargs)
        self.message = message


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
    debugprint = True

    def __init__(self, **kwargs):
        super(MMTKernel,self).__init__(**kwargs)
        self.mmtsession = requests.Session()
        self.adapter = requests.adapters.HTTPAdapter()
        self.mmtsession.mount('https://', self.adapter)
        self.mmtsession.mount('http://', self.adapter)
        self.headers = {'content-type' : 'application/json',
                        'content-encoding' : 'UTF-8'}
        try:
            response_dict = self.mmtsession.get(MMT_BASE_URL + '/:' + MMT_SERVER_EXTENSION+'?start',data = None,headers = self.headers, stream = True).json()
            sessionheader = { 'X-REPL-Session' : response_dict['session'] }
            self.headers = {**self.headers, **sessionheader}
        except Exception as e:
            pass

    def do_execute(self, code, silent, store_history=True,user_expressions=None,allow_stdin=False):
        try:
            response_dict = self.handle_request(code)
            message = response_dict['message']
            if not response_dict['success']:
                raise MMTError(message)
        # for connection errors
        except requests.exceptions.RequestException:
            message = self.wrap_errors('Unable to communicate with the MMT-Server')

        # for internal MMT errors
        except MMTError as e:
            message = self.wrap_errors('An internal MMT Error occured:')
            if self.debugprint:
                message += """
                <html>
                <div id="stacktrace"  style="display:none;"> """+e.message+"""</div>
                <input id="button" type="button" name="button" value="Show Stacktrace" onclick="toggle()" />
                <script>
                    function toggle() {
                      	var elem = document.getElementById('button')
                      	if(elem.value == "Show Stacktrace"){
                        	elem.value = "Hide Stacktrace";
                      		document.getElementById('stacktrace').style.display = "block";
                      	}
                        else {
                        	elem.value = "Show Stacktrace";
                        	document.getElementById('stacktrace').style.display = "none";
                        }
                    }
                </script>
                </html>"""
        # for all the other errors
        except Exception as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = self.get_stream_content(self.wrap_errors(template.format(type(e).__name__, e.args)))
        finally:
            if not silent:
                # send the response to the frontend
                self.send_response(self.iopub_socket, 'display_data',self.get_stream_content(message))
                return {'status': 'ok',
                # The base class increments the execution count
                'payload' : [],
                'execution_count': self.execution_count,
                'user_expressions': {},
                }

    """handles the POST requests to the MMT-Server"""
    def handle_request(self,code):
        binary_data = code.encode('UTF-8')
        return self.mmtsession.post(MMT_BASE_URL + '/:' + MMT_SERVER_EXTENSION,data = binary_data,headers = self.headers, stream = True).json()

    """marks errors red"""
    def wrap_errors(self,error):
        return '<p style="color:red;">'+error+'</p>'

    """called when the kernel is terminated"""
    def do_shutdown(self,restart):
        try:
            out = requests.get(MMT_BASE_URL + '/:' + MMT_SERVER_EXTENSION+'?quit',data = None,headers = self.headers, stream = True)
        except requests.exceptions.RequestException:
            pass


    """wraps the message into the stream_content format"""
    def get_stream_content(self,message):
        return {
        'data': {
            'text/html': message
        },
        'metadata': {},
        'transient': {},
        }


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=MMTKernel)
