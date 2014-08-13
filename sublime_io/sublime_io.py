import os
import sublime
import sublime_plugin
import subprocess
import time

# refresh without jitter
# figure out a way to move to end of file
# append data instead of having a file

DOUBLE = {'cols': [0.0, 0.5, 1.0],
          'rows': [0.0, 1.0],
          'cells': [[0, 0, 1, 1], [1, 0, 2, 1]]}

class SublimeIo(sublime_plugin.WindowCommand):
    def init(self, cmd):
        self.view = self.window.active_view()
        self.scheme = self.view.settings().get('color_scheme')
        self.output_path = os.path.join(sublime.packages_path(), '[output]')
        self.output_file = open(self.output_path, 'w')
        self.layout = self.window.layout()

        self.proc = subprocess.Popen(args = cmd,
                                     bufsize = 0,
                                     stdin = subprocess.PIPE,
                                     stdout = self.output_file,
                                     stderr = subprocess.STDOUT,
                                     shell = True,
                                     universal_newlines = True)
        self.start_time = time.time()

    def newlayout(self):
        self.output_view = self.window.open_file(self.output_path)
        
        self.output_view.set_scratch(True)
        self.output_view.set_read_only(True)
        self.window.set_layout(DOUBLE)
        self.window.run_command('move_to_group', {'group': 1})

    def input_panel(self):
        input_panel = self.window.show_input_panel('',
                                                   '',
                                                   self.on_done,
                                                   None,
                                                   self.on_cancel)
        input_panel.settings().set('color_scheme', self.scheme)

    def on_done(self, string):
        self.proc.stdin.write(string + '\n')
        self.proc.stdin.flush()
        self.input_panel()

    def on_cancel(self):
        self.proc.kill()
        self.output_view.close()
        self.window.set_layout(self.layout)

    def finish(self):
        while self.proc.poll() is None:
            self.output_view.run_command('revert')

        code = self.proc.poll()
        elapsed = time.time() - self.start_time

        if code:
            chars = '[Finished in %.1fs with exit code %d]' % (elapsed, code)
        else:
            chars = '[Finished in %.1fs]' % (elapsed)
        
        self.output_view.run_command('move_to', {'to': 'eof'})
        self.window.show_input_panel('', '', None, None, None)
        self.window.run_command('hide_panel')
        self.output_view.run_command('append', {'characters':  chars})

    def run(self):
        self.init('C:/Users/Music/Desktop/Python34/pythonw.exe')
        self.newlayout()
        self.input_panel()
        sublime.set_timeout_async(self.finish, 0)
        self.window.focus_view(self.view)
