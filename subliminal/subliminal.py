import sublime
import sublime_plugin
import subprocess
import time

# on output close exit process

class Subliminal(sublime_plugin.WindowCommand):
    def on_done(self, cmd):
        self.output = self.window.create_output_panel('output')

        self.output.settings().set('color_scheme', self.scheme)
        self.window.run_command('show_panel', {'panel': 'output.output'})
        sublime.set_timeout_async(lambda: self.read(cmd), 0)

    def read(self, cmd):
        proc = subprocess.Popen(args = cmd, bufsize = 0, stdout = subprocess.PIPE,
            shell = True, universal_newlines = True)
        start_time = time.time()

        while proc.poll() is None:
            self.output.run_command('append', {'characters':  proc.stdout.read(),
                'force': True, 'scroll_to_end': True})

        elapsed = time.time() - start_time
        exitcode = proc.poll()

        if exitcode:
            text = '[Finished in %.1fs with exit code %d]' % (elapsed, exitcode)
        else:
            text = '[Finished in %.1fs]' % elapsed

        self.output.run_command('append', {'characters':  text, 'force': True,
            'scroll_to_end': True})

    def run(self):
        self.scheme = self.window.active_view().settings().get('color_scheme')
        self.panel = self.window.show_input_panel('', '', self.on_done, None, None)
        
        self.panel.settings().set('color_scheme', self.scheme)
        self.panel.settings().set('syntax', 'Packages/Batch File/Batch File.tmLanguage')
