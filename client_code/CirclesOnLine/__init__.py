from ._anvil_designer import CirclesOnLineTemplate


def clamp(value, min_value, max_value):
    if not isinstance(value, (int, float)):
        value = 0
    return max(min_value, min(value, max_value))


class CirclesOnLine(CirclesOnLineTemplate):
    def __init__(self, **properties):
        self._height = 20
        self._n_circles_tot = 4
        self._n_circles_done = 0

        self.init_components(**properties)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        old_value = self._height
        self._height = clamp(value, 5, 1000)
        if self._height != old_value:
            self.canvas.height = self._height
            self.refresh()

    @property
    def n_circles_tot(self):
        return self._n_circles_tot

    @n_circles_tot.setter
    def n_circles_tot(self, value):
        old_value = self._n_circles_tot
        self._n_circles_tot = clamp(value, 2, 50)
        if self._n_circles_tot != old_value:
            self.refresh()

    @property
    def n_circles_done(self):
        return self._n_circles_done

    @n_circles_done.setter
    def n_circles_done(self, value):
        old_value = self._n_circles_done
        self._n_circles_done = clamp(value, 0, 50)
        if self._n_circles_done != old_value:
            self.refresh()

    def refresh(self):
        self.canvas.clear_rect(0, 0, self.canvas.get_width(), self.canvas.get_height())

        self.canvas.fill_style = self.line_color
        self.canvas.fill_rect(0, self.height / 2 - 2, self.canvas.get_width(), 4)

        r = self.height / 2
        x = r
        dx = (self.canvas.get_width() - self.height) / (self.n_circles_tot - 1)
        for i in range(int(self.n_circles_tot)):
            self.canvas.fill_style = (
                self.circle_done_color
                if self.n_circles_done and self.n_circles_done >= i + 1
                else self.circle_todo_color
            )
            self.canvas.begin_path()
            self.canvas.arc(x, r, r, 0, 2 * 3.14159)
            self.canvas.fill()

            self.canvas.fill_style = (
                self.text_done_color
                if self.n_circles_done and self.n_circles_done >= i + 1
                else self.text_todo_color
            )
            self.canvas.font = f"{int(r * 1.5)}px Arial"
            self.canvas.text_align = "center"
            self.canvas.text_baseline = "middle"
            self.canvas.fill_text(str(i + 1), x, r)

            x += dx

    def canvas_reset(self, **event_args):
        self.refresh()

    def canvas_show(self, **event_args):
        self.refresh()
