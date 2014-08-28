import os
import sublime
import sublime_plugin
import subprocess
import time

class Process(object):
    def __init__(self, cmd, path, classpath):
        env = os.environ.copy()
        env["PATH"] = os.path.expandvars("$PATH;" + path)
        env["CLASSPATH"] = os.path.expandvars("$CLASSPATH;" + classpath)
        self.proc = subprocess.Popen(
            args = cmd,
            bufsize = 0,
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            shell = True,
            env = env,
            )

    def kill(self):
        if sublime.platform() == "windows":
            subprocess.call("taskkill /PID %d" % self.proc.pid, shell = True)
        else:
            self.proc.terminate()

    def read(self):
        return os.read(self.proc.stdout.fileno(), 2 ** 15).decode().replace("\r\n", "\n").replace("\r", "\n")

    def write(self, string):
        os.write(self.proc.stdin.fileno(), string.encode())

    def poll(self):
        return self.proc.poll()

class Make(sublime_plugin.WindowCommand):
    def __init__(self, window):
        self.window = window
        self.view = self.window.active_view()
        self.layout = self.window.layout()
        self.scheme = self.view.settings().get("color_scheme")

    def set_layout(self, name):
        self.window.set_layout({"cols": [0.0, 0.5, 1.0], "rows": [0.0, 1.0],"cells": [[0, 0, 1, 1], [1, 0, 2, 1]]})
        self.window.focus_group(1)
        self.window.new_file()
        self.window.active_view().set_name("[%s]" % name)
        self.window.active_view().set_scratch(True)
        self.window.active_view().settings().set("scroll_past_end", False)

        self.output_view = self.window.active_view()

    def on_done(self, string):
        self.proc.write(string + "\n")
        self.output_view.run_command("append", {"characters": string + "\n"})
        self.output_view.run_command("move_to", {"to": "eof"})
        self.window.show_input_panel("", "", self.on_done, None, self.on_cancel).settings().set("color_scheme", self.scheme)

    def on_cancel(self):
        self.proc.kill()
        self.output_view.close()
        self.window.set_layout(self.layout)
        self.window.focus_view(self.view)

    def do(self):
        while self.proc.poll() is None:
           self.output_view.run_command("append", {"characters":  self.proc.read()}) 

        exitcode = self.proc.poll()
        elapsed = time.time() - self.start_time

        if exitcode:
            string = "[Finished in %.1fs with exit code %d]" % (elapsed, exitcode)
        else:
            string = "[Finished in %.1fs]" % elapsed
        
        self.output_view.run_command("append", {"characters":  string})
        self.window.show_input_panel("", "", None, None, None).settings().set("color_scheme", self.scheme)
        self.window.run_command("hide_panel")

    def run(self, cmd, path = "", classpath = ""):
        if cmd == "cmd":
            name = "cmd"
            # self.scheme = "Packages/Batch File/Batch File.tmLanguage"
        else:
            name = self.view.file_name()

        self.proc = Process(cmd, path, classpath)
        self.start_time = time.time()
        
        self.set_layout(os.path.basename(name))
        self.window.show_input_panel("", "", self.on_done, None, self.on_cancel).settings().set("color_scheme", self.scheme)
        sublime.set_timeout_async(self.do)
