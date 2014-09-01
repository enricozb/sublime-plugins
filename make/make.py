import os
import sublime
import sublime_plugin
import subprocess
import time

# set for shell if not windows along with syntax
# figure out why python does not work

class Process(object):
    def __init__(self, cmd, cwd, **env):
        env = dict(os.environ, **env)
        self.proc = subprocess.Popen(args = cmd, bufsize = 0, stdin = subprocess.PIPE,
            stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True,
            cwd = cwd, env = env)

    def kill(self):
        self.proc.stdin.close()
        self.proc.stdout.close()

        if sublime.platform() == 'windows':
            subprocess.call('taskkill /PID %d' % self.proc.pid, shell = True)
        else:
            self.proc.terminate()

    def read(self):
        return os.read(self.proc.stdout.fileno(), 2 ** 15).decode().replace('\r\n', '\n').replace('\r', '\n')

    def write(self, string):
        os.write(self.proc.stdin.fileno(), string.encode())

    def poll(self):
        return self.proc.poll()

class Make(sublime_plugin.WindowCommand):
    def set_layout(self, name):
        self.window.set_layout({'cols': [0.0, 0.5, 1.0], 'rows': [0.0, 1.0],'cells': [[0, 0, 1, 1], [1, 0, 2, 1]]})
        self.window.focus_group(1)
        self.window.new_file()
        self.window.active_view().set_name('[%s]' % name)
        self.window.active_view().set_scratch(True)
        self.window.active_view().settings().set('scroll_past_end', False)

        self.output_view = self.window.active_view()

    def on_done(self, string):
        self.proc.write(string + '\n')
        self.output_view.run_command('append', {'characters': string + '\n'})
        self.output_view.run_command('move_to', {'to': 'eof'})
        self.input_panel(self.on_done, None, self.on_cancel)

    def on_cancel(self):
        self.proc.kill()
        self.output_view.close()
        self.window.set_layout(self.layout)
        self.window.focus_view(self.view)

    def input_panel(self, on_done, on_change, on_cancel):
        panel = self.window.show_input_panel('', '', on_done, on_change, on_cancel)
        
        panel.settings().set('color_scheme', self.scheme)

    def do(self):
        while self.proc.poll() is None:
           self.output_view.run_command('append', {'characters':  self.proc.read()}) 

        exitcode = self.proc.poll()
        elapsed = time.time() - self.start_time

        if exitcode:
            string = '[Finished in %.1fs with exit code %d]' % (elapsed, exitcode)
        else:
            string = '[Finished in %.1fs]' % elapsed

        self.output_view.run_command('append', {'characters':  string})

    def run(self, cmd, **env):
        self.view = self.window.active_view()
        self.layout = self.window.layout()
        self.scheme = self.view.settings().get('color_scheme')
        self.name = self.view.file_name()

        self.proc = Process(cmd, os.path.dirname(self.name), **env)
        self.start_time = time.time()
        
        self.set_layout(os.path.basename(self.name))
        self.input_panel(self.on_done, None, self.on_cancel)
        sublime.set_timeout_async(self.do)
