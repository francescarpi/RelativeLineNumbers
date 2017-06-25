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


class RelativeLineNumbersEventListener(sublime_plugin.ViewEventListener):

    def __init__(self, view):
        self.view = view
        self.phantoms = sublime.PhantomSet(view, PACKAGE)
        self._render()

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

    def _render(self):

        settings = self.view.settings()
        enabled = settings.get(OPT_ENABLED, True)
        if not enabled:
            self.phantoms.update([])
            return

        phantoms = []
        self.phantoms.update([])

        current_line = self.view.rowcol(self.view.sel()[0].begin())[0]
        visible_lines = self.view.lines(self.view.visible_region())
        total_lines = len(visible_lines)

        lines = self.view.lines(
            sublime.Region(
                self.view.text_point(current_line - total_lines, 0),
                self.view.text_point(current_line + total_lines, 0)))

        for line in lines:
            line_number = self.view.rowcol(line.a)[0]

            phantoms.append(sublime.Phantom(
                line, 
                self._tpl(*self._value(line_number, current_line)),
                sublime.LAYOUT_INLINE))

        self.phantoms.update(phantoms)

    def on_modified(self):
        self._render()

    def on_activated(self):
        self._render()

    def on_selection_modified(self):
        self._render()
