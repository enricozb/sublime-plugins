import re
import sublime
import sublime_plugin

class F5(sublime_plugin.TextCommand):
    def run(self, edit, run):
        match = re.match(r"(.*, )*.+[.](.*?) ", self.view.scope_name(0))
        lang = match and match.groups()[1]

        cmd = {
            "java": 'java "{bn}"' if run else 'javac *.java',
            "c++": '"{bn}"' if run else 'g++ "{fn}" -o "{bn}"',
            "python": 'python -u "{fn}"',
            "js": 'java "{bn}"' if run else 'java org.mozilla.javascript.tools.jsc.Main "{fp}"',
        }.get(lang, "")

        path     = ("C:/Program Files*/Java/jdk*/bin;"
                    "{sd}/cygwin/bin;"
                    "{sd}/Python34;"
                    "{dp}")
        clspath  = ("{st}/Data/Packages/User/*.jar;"
                    ".;")
        inclpath = ("{sd}/cinder_0.8.6_vc2012/boost;"
                    "{sd}/cinder_0.8.6_vc2012/include;"
                    "{sd}/cinder_0.8.6_vc2012/src;"
                    ".;")

        if cmd:
            self.view.window().run_command("subliminal", {"cmd": cmd, "PATH": path,
                "CLASSPATH": clspath, "CPATH": inclpath})
        else:
            self.view.window().run_command("build")
