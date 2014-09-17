import glob
import os.path
import sublime
import sublime_plugin

class F5(sublime_plugin.TextCommand):
    def java(self, run):
        return 'java "{bn}"' if run else 'javac "{fp}"'

    def cpp(self, run):
        return '"{bn}"' if run else 'g++ "{fn}" -o "{bn}"'
    
    def py(self, run):
        return 'python -u "{fn}"'

    def js(self, run):
        return 'java "{bn}"' if run else 'java org.mozilla.javascript.tools.jsc.Main "{fp}"'

    def pde(self, run):
        # make sure dir is correct and return ""
        pass

    def run(self, edit, run):
        ex = os.path.splitext(self.view.file_name() or "")[1].strip(".").lower()
        path = "C:/Program Files*/Java/jdk*/bin;{sd}/*/bin;{sd}/Python*;{dp}"
        classpath = ".;{st}/Data/Packages/User/*.jar"
        cmd = getattr(self, ex, lambda run: "")(run)

        if cmd:
            self.view.window().run_command("subliminal", {"cmd": cmd, "PATH": path,
                "CLASSPATH": classpath})
        else:
            self.view.window().run_command("build")
