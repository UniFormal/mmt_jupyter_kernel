if __name__ == '__main__':
    import parser as Parser
else:
    from . import parser as Parser
import signal
import sys
import requests

def signal_handler(signal, frame):
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# base URL on which the MMT server runs
MMT_BASE_URL = 'http://localhost:9000/'

# MMT server extension that is used
MMT_SERVER_EXTENSION = 'interview'

class MMTShell():
    def __init__(self):
        # set server Extension
        self.extension = ':'+MMT_SERVER_EXTENSION+'/'

        # set default URI prefix
        self.URI_prefix = 'http://mathhub.info/'

        # the current theory or view
        self.currentScope = None

        # set default MMT namespace
        self.MMT_namespace = 'MitM/smglom/calculus'

        # set default meta theory
        self.metaTheory = 'http://cds.omdoc.org/urtheories?LF'


    def handleInputFromShell(self, input):
        parsedInput = Parser.splitInput(input)
        if parsedInput['error'] == True:
            return parsedInput['message']

        elif parsedInput['ShellAction'] == 'show namespace':
            return self.MMT_namespace

        elif parsedInput['ShellAction'] == 'show metaTheory':
            return self.metaTheory

        elif parsedInput['ShellAction'] == 'show scope':
            return self.currentScope

        elif parsedInput['ShellAction'] == 'set namespace':
            self.set_MMT_Namespace(parsedInput['data'][0])
            return 'set namespace to '+ self.MMT_namespace

        elif parsedInput['ShellAction'] == 'set metaTheory':
            self.set_MMT_metaTheory(parsedInput['data'][0])
            return 'set metaTheory to '+ self.metaTheory

        elif parsedInput['ShellAction'] == 'create theory':
            self.set_currentScope(parsedInput['data'][0])
            return self.create_theory_URL(parsedInput['data'][0])

        elif parsedInput['ShellAction'] == 'create view':
            self.set_currentScope(parsedInput['data'][0])
            return self.create_view_URL(parsedInput['data'][0],parsedInput['data'][1],parsedInput['data'][2])

        elif parsedInput['ShellAction'] == 'add term':
            theoryName = parsedInput['data'][1]
            if theoryName == None:
                theoryName = self.currentScope
            return self.add_term_URL(parsedInput['data'][0],theoryName)

        elif parsedInput['ShellAction'] == 'add declaration':
            theoryName = parsedInput['data'][1]
            if theoryName == None:
                theoryName = self.currentScope
            return self.add_declaration_URL(parsedInput['data'][0],theoryName)
        else:
            return 'Something went seriously wrong!'

    def handleInputFromKernel(self, input):
        parsedInput = Parser.splitInput(input)
        if parsedInput['error'] == True:
             return {
             'data': {
                'text/html':  parsedInput['message']
             },
              'metadata': {},
              'transient': {},
             }

        elif parsedInput['ShellAction'] == 'show namespace':
             return {
             'data': {
                'text/html':  self.MMT_namespace
             },
              'metadata': {},
              'transient': {},
             }

        elif parsedInput['ShellAction'] == 'show metaTheory':
             return {
             'data': {
                'text/html':  self.metaTheory
             },
              'metadata': {},
              'transient': {},
             }

        elif parsedInput['ShellAction'] == 'show scope':
            scope = self.currentScope
            if scope == None:
                scope = 'None'
            return {
            'data': {
               'text/html':  scope
            },
             'metadata': {},
             'transient': {},
            }

        elif parsedInput['ShellAction'] == 'set namespace':
            self.set_MMT_Namespace(parsedInput['data'][0])
            return {
            'data': {
               'text/html':  'set namespace to '+ self.MMT_namespace
            },
             'metadata': {},
             'transient': {},
            }

        elif parsedInput['ShellAction'] == 'set metaTheory':
            self.set_MMT_metaTheory(parsedInput['data'][0])
            return {
            'data': {
               'text/html':  'set metaTheory to '+ self.metaTheory
            },
             'metadata': {},
             'transient': {},
            }

        elif parsedInput['ShellAction'] == 'create theory':
            self.set_currentScope(parsedInput['data'][0])
            URL = self.create_theory_URL(parsedInput['data'][0])
            return {
            'data': {
                'text/html':  requests.get(URL).text
            },
             'metadata': {},
             'transient': {},
            }


        elif parsedInput['ShellAction'] == 'create view':
            self.set_currentScope(parsedInput['data'][0])
            URL = self.create_view_URL(parsedInput['data'][0],parsedInput['data'][1],parsedInput['data'][2])
            return {
            'data': {
                'text/html':  requests.get(URL).text
            },
             'metadata': {},
             'transient': {},
            }

        elif parsedInput['ShellAction'] == 'add term':
            theoryName = parsedInput['data'][1]
            if theoryName == None:
                theoryName = self.currentScope
            URL = self.add_term_URL(parsedInput['data'][0],theoryName)
            return {
            'data': {
                'text/html':  requests.get(URL).text
            },
             'metadata': {},
             'transient': {},
            }

        elif parsedInput['ShellAction'] == 'add declaration':
            theoryName = parsedInput['data'][1]
            if theoryName == None:
                theoryName = self.currentScope
            URL = self.add_declaration_URL(parsedInput['data'][0],theoryName)
            return {
            'data': {
                'text/html':  requests.get(URL).text
            },
             'metadata': {},
             'transient': {},
            }
        else:
            return 'Something went seriously wrong!'

    def create_theory_URL(self, theoryName):
        return MMT_BASE_URL + self.extension + 'new?theory=' + self.get_path(theoryName) + '&meta=' + self.metaTheory

    def create_view_URL(self, viewName, fromTheory, toTheory):
        return MMT_BASE_URL + self.extension + 'new?view=' + self.get_path(viewName) + '&from=' + self.get_path(fromTheory)+ '&to=' + self.get_path(toTheory)

    def add_term_URL(self,termName,theoryName):
        return MMT_BASE_URL + self.extension +'new?term=' +termName + '&cont=' + self.get_path(theoryName)

    def add_declaration_URL(self,declarationName,theoryName):
        return MMT_BASE_URL + self.extension +'new?decl=' +declarationName + '&cont=' + self.get_path(theoryName)


    # returns the MMT path / URI for a theory or view
    def get_path(self,name):
        return self.URI_prefix + self.MMT_namespace + '?' + name

    def http_request(self,URL):
        return requests.get(MMT_BASE_URL + self.extension + URL).text

    def set_currentScope(self,scope):
        self.currentScope = scope

    def set_MMT_Namespace(self, namespace):
        self.MMT_namespace = namespace

    def set_MMT_metaTheory(self,metaTheory):
        self.metaTheory = metaTheory

if __name__ == '__main__':
    shell = MMTShell()
    while(True):
        x = input()
        if x == 'q':
            break
        result = shell.handleInputFromShell(x)
        print(result)
