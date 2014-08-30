import glob
import os
import sublime
import sublime_plugin

class Peep(sublime_plugin.TextCommand):
    def run(self, edit):
        files = (os.path.dirname(view.file_name()) for window in sublime.windows() for view in window.views())
        files = sum((glob.glob(dp + '/*') for dp in files), [])
        files = filter(os.path.isfile, set(files))
        
        tolist = lambda file: [os.path.basename(file), file]
        key = lambda list: list[0].lower()

        items = sorted(map(tolist, files), key = key)
        index = items.index(tolist(self.view.file_name()))
        on_select = lambda i: self.view.window().open_file(items[index if i == -1 else i][1])

        self.view.window().show_quick_panel(items, on_select, 0, index)

