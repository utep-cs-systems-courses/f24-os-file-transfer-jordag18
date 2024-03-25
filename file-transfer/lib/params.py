from sys import argv
import sys

progName = "program"
if len(argv):
    progName = argv[0]
    del argv[0]

def parseParams(_switchesVarDefaults):
    global switchesVarDefaults
    paramMap = {}
    switchesVarDefaults = _switchesVarDefaults
    swVarDefaultMap = {}  # map from cmd switch to param var name
    for switches, param, default in switchesVarDefaults:
        for sw in switches:
            swVarDefaultMap[sw] = (param, default)
        paramMap[param] = default  # set default values
    try:
        while len(argv):
            sw = argv[0]; del argv[0]
            if sw in swVarDefaultMap:
                paramVar, defaultVal = swVarDefaultMap[sw]
                if defaultVal is not False:  # Check if the parameter expects a value
                    if argv:  # Check if there is a next argument
                        val = argv[0]; del argv[0]
                        paramMap[paramVar] = val
                    else:
                        raise Exception(f"Expected value after {sw}")
                else:
                    paramMap[paramVar] = True
            else:
                raise Exception(f"Unexpected argument: {sw}")
    except Exception as e:
        print(f"Problem parsing parameters (exception={e})")
        usage()
    return paramMap
        
def usage():
    print(f"{progName} usage:")
    for switches, param, default in switchesVarDefaults:
        for sw in switches:
            if default is not False:
                print(f" [{sw} {param}]   (default = {default})")
            else:
                print(f" [{sw}]   ({param} if present)")
    sys.exit(1)
