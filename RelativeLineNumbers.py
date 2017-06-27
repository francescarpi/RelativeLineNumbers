"""
File: RelativeLineNumbers.py
Author: Francesc Arpí @ 2017
"""

import sublime
import sublime_plugin

PACKAGE = "RelativeLineNumbers"
OPT_ENABLED = "relative_line_numbers_enabled"
OPT_COLOR = "relative_line_numbers_color"
OPT_COLOR_CURRENT = "relative_line_numbers_current_line_color"
OPT_CURRENT_CHAR = "relative_line_numbers_current_line_char"


class RelativeLineNumbersEventListener(sublime_plugin.ViewEventListener):

    def __init__(self, view):
        self.view = view
        self.phantoms = sublime.PhantomSet(view, PACKAGE)
        self._render()

    def _tpl(self, value, current):
        settings = self.view.settings()
        color = settings.get(OPT_COLOR, "gray")
        zero = settings.get(OPT_COLOR_CURRENT, "white")
        current_class = "current" if current else ""

        return """
            <body id="{package}">
                <style>
                    .value {{
                        color: {color};
                        margin-right: 10px;
                    }}
                    .current {{
                        color: {zero};
                    }}
                </style>
                <div class="value {current_class}">{value}</div>
            </body>
        """.format(**dict(
            package=PACKAGE,
            color=color,
            zero=zero,
            value=value,
            current_class=current_class))

    def _value(self, line_number, current_line, current_line_char):
        value, current = current_line_char, True
        if line_number < current_line:
            value, current = str(current_line - line_number), False
        elif line_number > current_line:
            value, current = str(line_number - current_line), False

        if len(value) == 1:
            value = "&nbsp;" + value

        return value, current

    def _render(self):

        settings = self.view.settings()
        enabled = settings.get(OPT_ENABLED, True)
        current_line_char = settings.get(OPT_CURRENT_CHAR, "0")
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
            value, current = self._value(
                line_number, current_line, current_line_char)

            phantoms.append(sublime.Phantom(
                line,
                self._tpl(value, current),
                sublime.LAYOUT_INLINE))

        self.phantoms.update(phantoms)

    def on_activated(self):
        self._render()

    def on_selection_modified(self):
        self._render()
