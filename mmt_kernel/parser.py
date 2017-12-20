import signal
import sys
def signal_handler(signal, frame):
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# def f(key,code)
#   return code.startswith[key+" "]
# def rest(key,code)
#   return code[len(key)+1:]

# ['createView'][]

# parses the input string into
# a dict like this
# {
#   'create view' : ["name","from","to"]
#   'create theory' : [name,metaTheory]
#   ....
# }
def splitInput(input):
    try:
        if input.startswith('show metaTheory'):
            return{
            'ShellAction' : 'show metaTheory',
            'error' : False,
            }

        elif input.startswith('show namespace'):
            return{
            'ShellAction' : 'show namespace',
            'error' : False,
            }

        elif input.startswith('show scope'):
            return{
            'ShellAction' : 'show scope',
            'error' : False,
            }

        elif input.startswith('set metaTheory'):
            if(len(input[len('set metaTheory')+1:]) == 0):
                raise ValueError
            return{
            # yes this is redundant...
            'ShellAction' : 'set metaTheory',
            'data' : [input[len('set metaTheory')+1:]],
            'error' : False,
            }

        elif input.startswith('set namespace'):
            if(len(input[len('set namespace')+1:]) == 0):
                raise ValueError
            return{
            # yes this is redundant...
            'ShellAction' : 'set namespace',
            'data' : [input[len('set namespace')+1:]],
            'error' : False,
            }

        elif input.startswith('create theory'):
            if(len(input[len('create theory')+1:]) == 0):
                raise ValueError
            return{
            'ShellAction' : 'create theory',
            'data' : [input[len('create theory')+1:]],
            'error' : False,
            }

        elif input.startswith('create view'):
            if(len(input[len('create view')+1:]) == 0):
                raise ValueError
            viewName, fromTheory, toTheory = input[len('create view')+1:].split(" ",2)
            return{
            'ShellAction' : 'create view',
            'data' : [viewName,fromTheory,toTheory],
            'error' : False,
            }


        elif input.startswith('add term'):
            try:
                termName, theory = input[len('add term')+1:].split(" ",1)
                return{
                'ShellAction' : 'add term',
                'data' : [termName,theory],
                'error' : False,
                }
            except ValueError:
                if(len(input[len('add term')+1:]) == 0):
                    raise ValueError
                theory = None
                termName = input[len('add term')+1:]
                return{
                'ShellAction' : 'add term',
                'data' : [termName,theory],
                'error' : False,
                }

        else:
            raise ValueError
    except ValueError:
        return{
            'error' : True,
            'message' : """
            <html>
            <body>
            <p style="color:red;">Invalid input! Valid options are:</p>
            <p style="color:red;">create view &ltView> </p>
            <p style="color:red;">create theory &ltTheory> </p>
            <p style="color:red;">add term &ltTerm></p>
            <p style="color:red;">add declaration &ltDeclaration> [&ltTheory>]</p>
            <p style="color:red;">infer in &ltTheory>/&ltView> &ltTerm> (currently not supported)</p>
            <p style="color:red;">show namespace</p>
            <p style="color:red;">show metaTheory</p>
            <p style="color:red;">show scope</p>
            <p style="color:red;">set namespace &ltNamespace></p>
            <p style="color:red;">set metaTheory &ltMetaTheory></p>
            </body>
            </html>""",


            # """Invalid input! Valid options are:
            # create view <View>
            # create theory <Theory>
            # add term <Term> [<Theory>]
            # add declaration <Declaration> [<Theory>]
            # infer in <Theory>/<View> <Term> (currently not supported)
            # show namespace
            # show metaTheory
            # show scope
            # set namespace <Namespace>
            # set metaTheory <metaTheory>""",
        }



def print_result(result):
    if result == None:
        return "No input!"
    else:
        for (k,v) in result.items():
            if type(v) is list:
                for s in v:
                    if(s == None):
                        print(k+" : None")
                    else:
                        print(k+" : "+s)
            else:
                print(k+" : "+v)


if __name__ == '__main__':
	while(True):
		x = input()
		if x == 'q':
			break
		res = splitInput(x)
		print_result(res)
		print()
