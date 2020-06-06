import py_compile

if __name__ == '__main__':
    py_compile.compile('PyLib.py', cfile = '..\ContrastApp\PyLib.pyc')
    input("ready")