import glob
import os.path
import sublime
import sublime_plugin

class Peep(sublime_plugin.WindowCommand):
    def on_select(self, files, i):
        if i != -1:
            self.window.open_file(files[i])

    def run(self):
        array = lambda file: [os.path.basename(file), file]
        key = lambda array: array[1].lower()

        files = (view.file_name() for window in sublime.windows() for view in window.views())
        files = (os.path.dirname(file) for file in files if file)
        files = (path for dir in files for path in glob.iglob("%s/*" % dir))
        files = sorted(set(path for path in files if os.path.isfile(path)), key = key)
        
        items = list(array(file) for file in files)

        self.window.show_quick_panel(items, lambda i : self.on_select(files, i))
