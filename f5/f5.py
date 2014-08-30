import functools
import glob
import os
import sublime
import sublime_plugin

class F5Command(sublime_plugin.TextCommand):
    def java(self, run):
        return 'java "{bn}"' if run else 'javac "{fp}"' 

    def cpp(self, run):
        return '"{bn}"' if run else 'g++ "{fp}" -o "{bn}"' 
    
    def py(self, run):
        return 'python -u "{fp}"'

    def pde(self, run):
        #place in dir and return ''
        pass

    def run(self, edit, run):
        fp = self.view.file_name()
        dp = os.path.dirname(fp)
        bn = os.path.splitext(os.path.basename(fp))[0]
        ex = os.path.splitext(os.path.basename(fp))[1].strip('.').lower()
        sd = os.path.dirname(os.path.dirname(sublime.executable_path()))
        
        path = [dp, 'C:/Program Files*/Java/jdk*/bin', '{sd}/*/bin', '{sd}/Python*']
        path = ';'.join(sum(map(glob.glob, path), []))
        classpath = '.;'

        cmd = getattr(self, ex, lambda run: '')(run).format(**locals())

        if cmd:
            self.view.window().run_command('make', {'cmd': cmd, 'env': {'path': path, 'classpath': classpath}})
        else:
            self.view.window().run_command('build')
