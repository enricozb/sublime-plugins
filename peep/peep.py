import glob
import os.path
import sublime
import sublime_plugin

class Peep(sublime_plugin.WindowCommand):
    def on_select(self, files, i):
        if i != -1:
            self.window.open_file(files[i])

    def run(self):
        array = lambda f: [os.path.basename(f), f]
        key = lambda array: array[1].lower()

        files = (v.file_name() for w in sublime.windows() for v in w.views())
        files = (os.path.dirname(f) for f in files if f)
        files = (p for d in files for p in glob.iglob("%s/*" % d))
        files = sorted(set(p for p in files if os.path.isfile(p)), key = key)
        
        items = list(array(f) for f in files)

        self.window.show_quick_panel(items, lambda i : self.on_select(files, i))
