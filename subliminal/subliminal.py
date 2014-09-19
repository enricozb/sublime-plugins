import glob
import os
import sublime
import sublime_plugin
import subprocess
import time

# implement restore_layout

class Process:
    def __init__(self, cmd, cwd, env):
        self.start_time = time.time()
        self.proc = subprocess.Popen(args = cmd, bufsize = 0, stdin = subprocess.PIPE,
            stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True,
            cwd = cwd or None, env = dict(os.environ, **env))

    def kill(self):
        self.proc.stdin.close()
        self.proc.stdout.close()

        if sublime.platform() == "windows":
            subprocess.call("taskkill /PID %d" % self.proc.pid, shell = True)
        else:
            self.proc.terminate()

    def read(self):
        bytes = os.read(self.proc.stdout.fileno(), 2 ** 15)

        try: 
            return bytes.decode().replace("\r\n", "\n").replace("\r", "\n")
        except UnicodeDecodeError:
            return bytes.decode("cp1252").replace("\r\n", "\n").replace("\r", "\n")

    def write(self, string):
        os.write(self.proc.stdin.fileno(), string.encode())

    def poll(self):
        return self.proc.poll()

class SubliminalCommand(sublime_plugin.WindowCommand):
    def update_vars(self, syntax):
        self.view = self.window.active_view()
        self.layout = self.window.layout()
        self.scheme = self.view.settings().get("color_scheme")
        self.syntax = syntax

        self.fp = self.view.file_name() or ""
        self.dp = os.path.dirname(self.fp)
        self.fn = os.path.basename(self.fp)
        self.bn = os.path.splitext(self.fn)[0]
        self.ex = os.path.splitext(self.fn)[1].strip(".").lower()
        self.st = os.path.dirname(sublime.executable_path())
        self.sd = os.path.dirname(self.st)

    def update_env(self, env):
        for var in env:
            env[var] = os.path.expandvars(env[var]).format(**vars(self)).split(";")
            env[var] = ";".join(dir for dirs in map(glob.glob, env[var]) for dir in dirs)

    def update_layout(self):
        self.output = self.window.new_file()

        self.window.set_layout({"cols": [0.0, 0.5, 1.0], "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]}) # test if necessary
        self.window.set_view_index(self.output, 1, 0)
        self.window.focus_view(self.view) # mvoe to bottom?
        
        self.output.set_scratch(True)
        self.output.set_name("[%s]" % self.fn)
        self.output.settings().set("word_wrap", True)
        self.output.settings().set("syntax", self.syntax)
        self.output.settings().set("scroll_past_end", False)
        self.output.settings().set("color_scheme", self.scheme)

    def update_output(self):
        while self.proc.poll() is None:
           self.output.run_command("append", {"characters":  self.proc.read()}) 

        elapsed = time.time() - self.proc.start_time
        exitcode = self.proc.poll()

        if exitcode:
            string = "[Finished in %.1fs with exit code %d]" % (elapsed, exitcode)
        else:
            string = "[Finished in %.1fs]" % elapsed

        self.output.run_command("append", {"characters":  string})

    def on_done(self, string):
        try:
            self.proc.write(string + "\n")
            self.output.run_command("append", {"characters": string + "\n"})
            self.output.run_command("move_to", {"to": "eof"})
            self.input_panel(self.on_done, self.on_cancel)
        except OSError:
            self.window.run_command("hide_panel")

    def on_cancel(self):
        self.proc.kill()
        self.output.close()
        self.window.set_layout(self.layout)
        self.window.focus_view(self.view)

    def input_panel(self, on_done, on_cancel):
        panel = self.window.show_input_panel("", "", on_done, None, on_cancel)
        
        panel.settings().set("color_scheme", self.scheme)
        panel.settings().set("syntax", self.syntax)
    
    def run(self, cmd, syntax = "Packages/Text/Plain text.tmLanguage", **env):
        self.update_vars(syntax)
        self.update_env(env)

        cmd = cmd.format(**vars(self))
        self.proc = Process(cmd, self.dp, env)

        self.update_layout()
        self.input_panel(self.on_done, self.on_cancel)

        sublime.set_timeout_async(self.update_output)
        sublime.status_message('running "%s"' % cmd)
