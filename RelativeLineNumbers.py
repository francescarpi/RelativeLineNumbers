"""
File: RelativeLineNumbers.py
Author: Francesc Arpí @ 2017
"""

import sublime
import sublime_plugin

PACKAGE = "RelativeLineNumbers"
OPT_ENABLED = "relative_line_numbers_enabled"
OPT_COLOR = "relative_line_numbers_color"
OPT_COLOR_ZERO = "relative_line_numbers_zero_color"


class RelativeLineNumbersCommand(sublime_plugin.TextCommand):
    """
    run: view.run_command('relative_line_numbers')
    """

    def __init__(self, *args, **kwargs):
        super(RelativeLineNumbersCommand, self).__init__(*args, **kwargs)
        self._visible = False
        self.phantoms = sublime.PhantomSet(self.view, PACKAGE)

    def run(self, edit, *args, **kwargs):
        self._visible = not self._visible

        if self._visible:
            self._render()
        else:
            self._clear()

    def _tpl(self, *kwargs):
        settings = self.view.settings()
        color = settings.get(OPT_COLOR, "gray")
        zero = settings.get(OPT_COLOR_ZERO, "white")

        return """
            <body id="{0}">
                <style>
                    .value {{
                        color: {1};
                        margin-right: 10px;
                    }}
                    .value0 {{
                        color: {2};
                    }}
                </style>
                <div class="value value{3}">{4}</div>
            </body>
        """.format(PACKAGE, color, zero, *kwargs)

    def _value(self, line_number, current_line):
        value = 0
        if line_number < current_line:
            value = current_line - line_number
        elif line_number > current_line:
            value = line_number - current_line

        valuestr = str(value)
        if value < 10:
            valuestr = "&nbsp;" + valuestr

        return value, valuestr

    def _clear(self):
        self.phantoms.update([])

    def _render(self):

        settings = self.view.settings()
        enabled = settings.get(OPT_ENABLED, True)
        self._clear()
        if not enabled:
            return

        phantoms = []
        current_line = self.view.rowcol(self.view.sel()[0].begin())[0]
        lines = self.view.lines(self.view.visible_region())

        for line in lines:
            line_number = self.view.rowcol(line.a)[0]

            phantoms.append(sublime.Phantom(
                line,
                self._tpl(*self._value(line_number, current_line)),
                sublime.LAYOUT_INLINE))

        self.phantoms.update(phantoms)
