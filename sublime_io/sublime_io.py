import os
import sublime
import sublime_plugin
import subprocess
import time

DOUBLE = {
           'cols': [0.0, 0.5, 1.0],
           'rows': [0.0, 1.0],
           'cells': [[0, 0, 1, 1], [1, 0, 2, 1]]
         }

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
        self.window.set_layout(DOUBLE)
        self.window.run_command('move_to_group', {'group': 1})
        self.window.focus_view(self.view)

    def input_panel(self):
        input_panel = self.window.show_input_panel('',
                                                   '',
                                                   self.on_done,
                                                   self.on_change,
                                                   self.on_cancel)
        input_panel.settings().set('color_scheme', self.scheme)

    def on_done(self, string):
        self.proc.stdin.write(string + '\n')
        self.proc.stdin.flush()
        self.input_panel()

    def on_change(self, string):
        self.output_view.run_command('revert')

    def on_cancel(self):
        self.proc.kill()
        self.output_view.close()
        self.window.set_layout(self.layout)

    def finish(self):
        elapsed = time.time() - self.start_time
        code = self.proc.wait()

        if code:
            string = '[Finished in %.1fs with exit code %d]' % (elapsed, code)
        else:
            string = '[Finished in %.1fs]' % (elapsed)
        open(self.output_path, 'a').write(string)
        self.output_view.run_command('revert')
        self.output_view.run_command('move_to', {'to': 'eof'})

    def run(self):
        self.init('python C:/Users/Music/Desktop/script.py')
        self.newlayout()
        self.input_panel()
        sublime.set_timeout_async(self.finish, 0)
