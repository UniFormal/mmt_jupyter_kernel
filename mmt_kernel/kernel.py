import sys
import os
import ipywidgets
import subprocess
import time

# TODO clean up imports
from jupyter_client import KernelClient

from .mmt import *
from .utils import to_display_data
from .utils import check_port, generate_port

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from IPython.display import display

from traitlets import Instance, Type, Any, List, Bool
from ipykernel.kernelbase import Kernel
from ipykernel.comm import CommManager
from ipykernel.zmqshell import ZMQInteractiveShell

MMT_JAR_LOCATION = os.getenv('MMT_JAR_LOCATION', os.path.expanduser("~/MMT/deploy/mmt.jar"))
MMT_MSL_LOCATION = os.getenv('MMT_MSL_LOCATION', os.path.expanduser("~/MMT/deploy/startup.msl"))
MMT_PY4J_HOST = os.getenv('MMT_PY4J_HOST', '127.0.0.1')
MMT_PY4J_PORT = os.getenv('MMT_PY4J_PORT', None)

# ----------------------------------  WIDGET  ----------------------------------
class Widget:
    """A wrapper class for Jupyter Widgets"""
    def __init__(self, widget, kernel, ID):
        # in case we want to reference any of these instance variables
        # we need to define a get function (also on scala side) for it (see e.g. ID)
        self.kernel = kernel
        self.jupwid = widget
        self.keys = {}
        self.ID = ID

    def set(self, key, value):
        """Sets key to value. Returns this widget to allow chaining."""
        self.keys[key] = value
        setattr(self.jupwid,key,value)
        return self

    def get(self, key):
        """Returns the value to given key"""
        return getattr(self.jupwid,key)
    
    def getAsFloat(self,key):
        """Necessary for the right datatype in Scala""" 
        return self.get(key)
    
    def getAsBool(self,key):
        """Necessary for the right datatype in Scala""" 
        return self.get(key)
    
    def getAsString(self,key):
        """Neccessary for the right datatype in Scala"""
        return self.get(key)
    
    def getID(self):
        return self.ID
    
    def observe(self, callback, key):
        """Registers a callback to the widget, that is called 
        when the specified key changes. Returns this widget
        to allow chaining."""
        def change_owner_and_observe(d):
            d.update({"owner" : self}) 
            callback(self.kernel, d)
        self.jupwid.observe(change_owner_and_observe ,key)
        return self

    def on_click(self,callback):
        """Registers a callback to the widget, that is called when it is clicked.
        Returns this widget to allow chaining."""
        self.jupwid.on_click(lambda b: callback(self.kernel,self))
        return self

    def toString(self):
        return repr(self)
    
    def display(self):
        """Displays this widget. Returns this widget to allow chaining."""
        display(self.jupwid)
        return self

    def close(self):
        """Closes this widget and removes it from the notebook"""
        self.jupwid.close()

    class Java:
        implements = ["info.kwarc.mmt.python.WidgetPython"]


# ----------------------------------  KERNEL  ----------------------------------
widgets = {}
wcounter = 0

class JupyterKernel(Kernel):
    implementation = 'MMT'
    implementation_version = '1.3'
    language = 'mmt'
    language_version = '0.1'
    language_info = {
        'name': 'mmt',
        'mimetype': 'text/mmt',
        'file_extension': '.mmt',
    }
    banner = "MMT Kernel"
        

    shell = Instance('IPython.core.interactiveshell.InteractiveShellABC', allow_none=True)
    shell_class = Type(ZMQInteractiveShell)

    use_experimental_completions = Bool(True,
        help="Set this flag to False to deactivate the use of experimental IPython completion APIs.",
        ).tag(config=True)

    user_module = Any()
    gateway = Any()
    scala = Any()
    msg = Any()

    def _user_module_changed(self, name, old, new):
        if self.shell is not None:
            self.shell.user_module = new

    user_ns = Instance(dict, args=None, allow_none=True)

    def _user_ns_changed(self, name, old, new):
        if self.shell is not None:
            self.shell.user_ns = new
            self.shell.init_user_ns()

    def __init__(self, **kwargs):
        super(JupyterKernel, self).__init__(**kwargs)
        # set up the shell
        self.shell = self.shell_class.instance(parent=self,
                                               profile_dir=self.profile_dir,
                                               user_module=self.user_module,
                                               user_ns=self.user_ns,
                                               kernel=self,
                                               )
        self.shell.displayhook.session = self.session
        self.shell.displayhook.pub_socket = self.iopub_socket
        self.shell.displayhook.topic = self._topic('execute_result')
        self.shell.display_pub.session = self.session
        self.shell.display_pub.pub_socket = self.iopub_socket

        # set up and attach comm_manager to the shell
        self.comm_manager = CommManager(parent=self, kernel=self)
        self.shell.configurables.append(self.comm_manager)
        comm_msg_types = ['comm_open', 'comm_msg', 'comm_close']
        for msg_type in comm_msg_types:
            self.shell_handlers[msg_type] = getattr(
                self.comm_manager, msg_type)
      
        # we use the session ID we get from the Jupyter session
        self.sessionID = str(self.session.session)
        self.msg = "start"

        port = self._spawn_or_connect()

        # wait for the port to open
        while not check_port(MMT_PY4J_HOST, port):
            print("Port not open")
            sys.stdout.flush()
            time.sleep(1)
        
        self.gateway = getJavaGateway(MMT_PY4J_HOST, port)
        controller = self.gateway.entry_point
        setupJavaObject(self.gateway)

        # connect to MMT via Py4JGateway and load the JupyterKernel extension
        self.scala = controller.extman().addExtension("info.kwarc.mmt.python.JupyterKernel", toScalaList(self.gateway,[]))
        self.scala.processRequest(self, self.sessionID,"start")
        self.py4jConnectionFailed = False
    
    def _spawn_or_connect(self):
        """ Spawns a new MMT instance or connects to it """

        # if the user provided a port via the environment variables
        # just return it
        if MMT_PY4J_PORT is not None:
            return int(MMT_PY4J_PORT)
        
        # if not spawn mmt on a new port
        else:
            return self._spawn_mmt()

    
    def _spawn_mmt(self):
        """ Spawns a new MMT instance """
        
        # generate a port on which to run MMT
        port = generate_port()
        
        LOG_FILE_LOCATION = os.path.join(os.path.expanduser("~"), "logs", "mmt-%s.log" % (port))
        if MMT_MSL_LOCATION:
            # start MMT with explicit MSL file
            MMT_ARGS = [
                "java", "-jar", MMT_JAR_LOCATION, 
                "--file", MMT_MSL_LOCATION,
                "-w", "log file %s ; extension info.kwarc.mmt.python.Py4JGateway %s" % (LOG_FILE_LOCATION, port)
            ]
        else:
            # start MMT without or with implicit MSL file which is located in the same folder as the mmt.jar
            MMT_ARGS = [
                "java", "-jar", MMT_JAR_LOCATION,
                "-w", "log file %s ; extension info.kwarc.mmt.python.Py4JGateway %s" % (LOG_FILE_LOCATION, port)
            ]
        # start MMT
        self.mmt = subprocess.Popen(MMT_ARGS,preexec_fn=os.setsid,stdin=subprocess.PIPE)

        # and return the port
        return port


  
    def start(self):
        self.shell.exit_now = False
        super(JupyterKernel, self).start()

    def set_parent(self, ident, parent):
        """Overridden from parent to tell the display hook and output streams
        about the parent message.
        """
        super(JupyterKernel, self).set_parent(ident, parent)
        self.shell.set_parent(parent)

    def init_metadata(self, parent):
        """Initialize metadata.
        Run at the beginning of each execution request.
        """
        md = super(JupyterKernel, self).init_metadata(parent)
        # FIXME: remove deprecated ipyparallel-specific code
        # This is required for ipyparallel < 5.0
        md.update({
            'dependencies_met': True,
            'engine': self.ident,
        })
        return md

    
    def do_complete(self,code,cursorPos):
        """Autocompletion when the user presses tab"""
        # load the shortcuts from the unicode-latex-map
        charMapPath = os.path.dirname(os.path.realpath(__file__))
        shortcuts = {}
        with open(os.path.join(charMapPath,'unicode-latex-map'), 'r', encoding='utf-8') as charMap:
            for line in charMap:
                line = line.replace('j','',1)
                line = line.replace('\n','',1)
                st, repl = line.split("|", 1)
                shortcuts[st] = repl

        # use them for tab-completion
        for k,v in shortcuts.items():
            if code[cursorPos-len(k)-1:cursorPos] == "\\"+k:
                return  {
                    'matches' : [v],
                    'cursor_end' : cursorPos,
                    'cursor_start' : cursorPos-len(k)-1,
                    'metadata' : {},
                    'status' : 'ok'
                }


    def do_execute(self, code, silent=False, store_history=True, user_expressions=None, allow_stdin=True):
        """Called when the user inputs code"""
        if self.py4jConnectionFailed:
            self.send_response(self.iopub_socket, 'display_data',to_display_data(self.msg))
        else:
            message = None
            response = self.scala.processRequest(self, self.sessionID,code)
            if "message" in response:
                message = to_display_data(response["message"])
            if "element" in response:
                message = to_display_data(response["element"])
            if "omdoc" in response:
                message = to_display_data(response["message"],response['omdoc'])
            if message:
                self.send_response(self.iopub_socket, 'display_data',message)

            
        return {'status': 'ok',
                # The base class increments the execution count
                'payload': [],
                'execution_count': self.execution_count,
                'user_expressions': {},
                }
  
    def do_shutdown(self,restart):
        """Called when the kernel is terminated"""
        self.scala.processRequest(self, self.sessionID,"quit")
        self.gateway.close(close_callback_server_connections=True)

        # close mmt if it was a process to begin
        if self.mmt is not None:
            self.mmt.stdin.write(b"exit\n")
            self.mmt.communicate()[0]
            self.mmt.stdin.close()
            self.mmt.kill()
            self.mmt = None


    def makeWidget(self, kind):
        """Creates a widget and registers it in the Kernel"""
        w = getattr(ipywidgets,kind)()
        # this is necessary for the Py4JGateway to identify the widget objects on Scala side
        setattr(w,"_get_object_id", lambda: repr(self))
        global wcounter
        ID = str(wcounter)
        wcounter = wcounter +1
        widgets.update({ID : w})
        return Widget(w, self, ID)
    
    def makePWidget(self, kind, PythonParamDict):
        """Creates a parameterized widget and registers it in the Kernel"""
        args = self.toPythonDict(PythonParamDict)
        w = getattr(ipywidgets,kind)(**args)
        setattr(w,"_get_object_id", lambda: repr(self))
        global wcounter
        ID = str(wcounter)
        wcounter = wcounter +1
        widgets.update({ID : w})
        return Widget(w, self, ID)

    def display(self,wids):
        """Displays a single, or a list of widgets"""
        if isinstance(wids, py4j.java_collections.JavaList):
            for wid in wids:
                wid.display()
        else:
            display(wids)  
    
    # TODO maybe move this somewhere else
    def toPythonDict(self,PythonParamDict):
        """Translates the Scala datastructure PythonParamDict to a python dict"""
        pythonDict = {}
        for key in PythonParamDict:
            value = PythonParamDict[key]
            if isinstance(value, py4j.java_gateway.JavaObject):
                pythonList = []
                for item in value:
                    if isinstance(item, py4j.java_gateway.JavaObject): 
                        # Problem here: we cannot distinguish between Scala Objects
                        # because they're wrapped in some Proxy Objects as you can see
                        # when you comment in the following line 
                        # display(str(item.getClass()))
                        pythonList.append(widgets[item.getID()]) 
                    else:
                        pythonList.append(item)
                pythonDict.update({key : pythonList})
            else:
                pythonDict.update({key : value})
        return pythonDict
    
    def toString(self):
        return str(self)

    # annotation for Py4J
    class Java:
        implements = ["info.kwarc.mmt.python.JupyterKernelPython"]


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=JupyterKernel)
