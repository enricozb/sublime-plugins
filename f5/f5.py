import glob
import os
import sublime
import sublime_plugin

class F5(sublime_plugin.TextCommand):
    def __init__(self, view):
        self.view = view
        self.fn = os.path.basename(self.view.file_name() or '')
        self.bn = os.path.splitext(self.fn)[0]
        self.ex = os.path.splitext(self.fn)[1].strip('.').lower()
        self.sd = os.path.dirname(os.path.dirname(sublime.executable_path()))

    def java(self, run):
        return 'java "{bn}"' if run else 'javac *.java'

    def cpp(self, run):
        return '"{bn}"' if run else 'g++ "{fn}" -o "{bn}"' 
    
    def py(self, run):
        return 'python -u "{fn}"'

    def pde(self, run):
        #place in dir and return ''
        pass

    def run(self, edit, run):
        classpath = '.;'
        path = 'C:/Program Files*/Java/jdk*/bin;{sd}/*/bin;{sd}/Python*;'
        path = map(glob.glob, path.format(**vars(self)).split(';'))
        path = ';'.join(dir for dirs in path for dir in dirs)
        cmd = getattr(self, self.ex, lambda run: '')(run).format(**vars(self))

        if cmd:
            self.view.window().run_command('make', {'cmd': cmd,
                'PATH': path, 'CLASSPATH': classpath})
        else:
            self.view.window().run_command('build')
