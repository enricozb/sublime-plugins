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

    def set_layout(self):
        self.window.set_layout({"cols": [0.0, 0.5, 1.0], "rows": [0.0, 1.0],"cells": [[0, 0, 1, 1], [1, 0, 2, 1]]})
        self.window.focus_group(1)
        self.window.new_file()
        self.window.active_view().set_name("[output]")
        self.window.active_view().set_scratch(True)

        self.output_view = self.window.active_view()

    def on_done(self, string):
        self.proc.write(string + "\n")
        self.output_view.run_command("append", {"characters": string + "\n", "force": True, "scroll_to_end": True})
        self.window.show_input_panel("", "", self.on_done, None, self.on_cancel).settings().set("color_scheme", self.scheme)

    def on_cancel(self):
        self.proc.kill()
        self.window.focus_view(self.view)

    def do(self):
        while self.proc.poll() is None:
           self.output_view.run_command("append", {"characters":  self.proc.read(), "force": True, "scroll_to_end": True}) 

        exitcode = self.proc.poll()
        elapsed = time.time() - self.start_time

        if exitcode:
            string = "[Finished in %.1fs with exit code %d]" % (elapsed, exitcode)
        else:
            string = "[Finished in %.1fs]" % elapsed
        
        self.output_view.run_command("append", {"characters":  string, "force": True, "scroll_to_end": True})
        self.window.run_command("hide_panel")

    def run(self, cmd = "python -u C:/Users/Music/Desktop/script.py", path = "", classpath = ""):
        self.proc = Process(cmd, path, classpath)
        self.start_time = time.time()
        
        self.set_layout()
        self.window.show_input_panel("", "", self.on_done, None, self.on_cancel).settings().set("color_scheme", self.scheme)
        sublime.set_timeout_async(self.do)
