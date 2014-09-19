import re
import sublime
import sublime_plugin

class F5(sublime_plugin.TextCommand):
    def run(self, edit, run):
        match = re.search(r"(?<=[.]).*?(?= )", self.view.scope_name(0))
        lang = match and match.group()
        cmd = {
            "java": 'java "{bn}"' if run else 'javac "{fp}"',
            "c++": '"{bn}"' if run else 'g++ "{fn}" -o "{bn}"',
            "python": 'python -u "{fn}"',
            "js": 'java "{bn}"' if run else 'java org.mozilla.javascript.tools.jsc.Main "{fp}"',
        }.get(lang, "")

        path = "C:/Program Files*/Java/jdk*/bin;{sd}/*/bin;{sd}/Python*;{dp}"
        classpath = ".;{st}/Data/Packages/User/*.jar"

        if cmd:
            self.view.window().run_command("subliminal", {"cmd": cmd, "PATH": path,
                "CLASSPATH": classpath})
        else:
            self.view.window().run_command("build")
