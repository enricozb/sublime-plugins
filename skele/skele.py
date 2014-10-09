import re
import sublime
import sublime_plugin

java = '''import java.io.*;
import java.util.*;

public class ${TM_FILENAME/(.*)[.](.*)/$1/g} {
    public static void main(String[] args) throws IOException {
        $1;
    }
}
'''

cpp = '''#include <cstdio>

int main(int argc, char* argv[]) {
    $1;
}
'''

python = '''def main():
    pass

main()
'''

class Skeleton(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        match = re.match(r"(.*, )*.+[.](.*?) ", view.scope_name(0))
        lang = match and match.groups()[1]

        snippet = {
            "java": java,
            "c++": cpp,
            "python": python
        }.get(lang, "")

        if view.size() == 0 and snippet:
            view.sel().add(sublime.Region(0, view.size()))
            view.run_command("insert_snippet", {"contents": snippet})
