import os
import sublime
import sublime_plugin

class PickScheme(sublime_plugin.WindowCommand):
    def pull(self, pat, dst):
        name = os.path.basename(self.settings.get('color_scheme'))
        root = os.path.dirname(sublime.packages_path())
        exists = lambda file: os.path.exists(os.path.join(root, file))

        for res in filter(exists, sublime.find_resources(pat)):
            os.renames(
                        os.path.join(root, res),
                        os.path.join(root, dst, os.path.basename(res))
                      )

        self.settings.set('color_scheme', sublime.find_resources(name)[0])

    def run(self):
        self.settings = sublime.load_settings('Preferences.sublime-settings')
        list = lambda res: [os.path.basename(res).split('.')[0], res]

        self.pull('*.tmTheme', 'Packages/User/Color Schemes')

        items = map(list, sublime.find_resources('*.tmTheme'))
        items = sorted(items, key = lambda list: list[0].lower())
        
        index = items.index(list(self.settings.get('color_scheme')))

        on_highlight = lambda i: self.settings.set('color_scheme', items[index if (i is -1) else i][1])

        on_select = lambda i: (on_highlight(i), sublime.save_settings('Preferences.sublime-settings'))
        
        self.window.show_quick_panel(items, on_select, 0, index, on_highlight)
