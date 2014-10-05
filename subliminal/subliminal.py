import glob
import os
import sublime
import sublime_plugin
import subprocess
import time

output  = None
pointer = None
process = None

class Process():
    def __init__(self, cmd, cwd, env):
        self.start_time = time.time()
        self.proc = subprocess.Popen(args = cmd, bufsize = 0, stdin = subprocess.PIPE,
            stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True,
            cwd = cwd, env = env)

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

class Subliminal(sublime_plugin.TextCommand):
    def update(self, cmd, env):
        fp = self.view.file_name() or ""
        dp = os.path.dirname(fp)
        fn = os.path.basename(fp)
        bn = os.path.splitext(fn)[0]
        ex = os.path.splitext(fn)[1].strip(".").lower()
        st = os.path.dirname(sublime.executable_path())
        sd = os.path.dirname(st)

        for var in env:
            env[var] = os.path.expandvars(env[var]).format(**locals()).split(";")
            env[var] = ";".join(path for iglob in map(glob.iglob, env[var]) for path in iglob)

        return cmd.format(**locals()), dp

    def layout(self, syntax, view):
        view.settings().set("word_wrap", True)
        view.settings().set("syntax", syntax)
        view.settings().set("scroll_past_end", False)
        view.settings().set("color_scheme", self.view.settings().get("color_scheme"))
        self.view.window().run_command("show_panel", {"panel": "output."})
        self.view.window().focus_view(view)

        return view

    def output(self, view, proc):
        global output, pointer, process
        
        while proc.poll() is None:
            view.run_command("append", {"characters":  proc.read()})
            view.run_command("move_to", {"to":  "eof"})

            pointer = view.size()

        elapsed = time.time() - proc.start_time
        exitcode = proc.poll()

        if exitcode:
            string = "[Finished in %.1fs with exit code %d]" % (elapsed, exitcode)
        else:
            string = "[Finished in %.1fs]" % elapsed

        view.run_command("append", {"characters":  string})

        # reassign to None once finished to allow Subliminal to be run again
        output = pointer = process = None

    def run(self, edit, cmd, syntax = "Packages/Text/Plain text.tmLanguage", **env):
        global process, output

        # prevents Subliminal from being run multiple times at once
        if output is pointer is process is None:
            cmd, dp = self.update(cmd, env)
            process = Process(cmd, dp or None, env)
            output  = self.layout(syntax, self.view.window().create_output_panel(""))

            sublime.set_timeout_async(lambda: self.output(output, process))
            sublime.status_message('running cmd "%s"' % cmd)

class Listener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if view == output:
            if key == "write":
                process.write(output.substr(sublime.Region(pointer, output.size())) + "\n")
            if key == "kill":
                process.kill()
