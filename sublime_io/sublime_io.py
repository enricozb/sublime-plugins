import os
import sublime
import sublime_plugin
import subprocess
import time

# proc.kill not working

class Del(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.replace(edit, self.view.line(self.view.size()), '')

class SublimeIo(sublime_plugin.WindowCommand):
    def init(self, args):
        self.view = self.window.active_view()
        self.scheme = self.view.settings().get('color_scheme')
        self.layout = self.window.layout()
        self.start_time = time.time()
        self.proc = subprocess.Popen(args = args,
                                     stdin = subprocess.PIPE,
                                     stdout = subprocess.PIPE,
                                     stderr = subprocess.STDOUT,
                                     shell = True,
                                     universal_newlines = True)

    def set_layout(self):
        self.window.set_layout({'cols': [0.0, 0.5, 1.0], 'rows': [0.0, 1.0], 'cells': [[0, 0, 1, 1], [1, 0, 2, 1]]})
        self.window.focus_group(1)
        self.window.new_file()
        self.window.active_view().set_name('[output]')
        self.window.active_view().set_scratch(True)

        self.output_view = self.window.active_view()

    def input_panel(self):
        self.window.show_input_panel('', '', self.on_done, self.on_change, self.on_cancel).settings().set('color_scheme', self.scheme)

    def on_done(self, text):
        self.output_view.run_command('append', {'characters': '\n', 'force': True, 'scroll_to_end': True})
        self.proc.stdin.write(text + '\n')
        self.proc.stdin.flush()
        self.input_panel()

    def on_change(self, text):
        self.output_view.run_command('del')
        self.output_view.run_command('append', {'characters':  text, 'force': True, 'scroll_to_end': True})

    def on_cancel(self):
        self.proc.kill()
        print('exit', self.proc.poll())
        # self.output_view.close()
        # self.window.set_layout(self.layout)

    def async(self):
        while self.proc.poll() is None:
            text = os.read(self.proc.stdout.fileno(), 2 ** 15).decode().replace('\r\n', '\n').replace('\r', '\n')
            self.output_view.run_command('append', {'characters':  text, 'force': True, 'scroll_to_end': True})

        exitcode = self.proc.poll()
        elapsed = time.time() - self.start_time

        if exitcode:
            text = '[Finished in %.1fs with exit code %d]' % (elapsed, exitcode)
        else:
            text = '[Finished in %.1fs]' % (elapsed,)
        
        self.window.run_command('hide_panel')
        self.output_view.run_command('append', {'characters':  text, 'force': True, 'scroll_to_end': True})

    def run(self):
        self.set_layout()
        self.init(['java', 'script'])
        self.input_panel()
        sublime.set_timeout_async(self.async, 0)
        self.window.focus_view(self.view)
