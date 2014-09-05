
import glob
import os.path
import sublime
import sublime_plugin

class F5(sublime_plugin.TextCommand):
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
        fp = self.view.file_name() or ''
        dp = os.path.dirname(fp)
        fn = os.path.basename(fp)
        bn = os.path.splitext(fn)[0]
        ex = os.path.splitext(fn)[1].strip('.').lower()
        sd = os.path.dirname(os.path.dirname(sublime.executable_path()))

        print(locals())

        classpath = '.;'
        path = 'C:/Program Files*/Java/jdk*/bin;{sd}/*/bin;{sd}/Python*;{dp}'
        path = map(glob.glob, path.format(**locals()).split(';'))
        path = ';'.join(dir for dirs in path for dir in dirs)
        cmd = getattr(self, ex, lambda run: '')(run).format(**locals())

        if cmd:
            self.view.window().run_command('make', {'cmd': cmd, 'PATH': path,
                'CLASSPATH': classpath})
        else:
            self.view.window().run_command('build')
