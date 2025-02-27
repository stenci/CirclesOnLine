from ._anvil_designer import CirclesOnLineTemplate
import math


def clamp(value, min_value, max_value):
    if not isinstance(value, (int, float)):
        value = 0
    return max(min_value, min(value, max_value))


def dist_point_point(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


class CirclesOnLine(CirclesOnLineTemplate):
    def __init__(self, **properties):
        self._height = 20
        self._n_circles_tot = 4
        self._n_circles_done = 0
        self.mouse_x = -1
        self.mouse_y = -1

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

        n_circle = None
        r = self.height / 2
        x = r
        dx = (self.canvas.get_width() - self.height) / (self.n_circles_tot - 1)
        for i in range(int(self.n_circles_tot)):
            if self.n_circles_done and self.n_circles_done >= i + 1:
                circle_color = self.circle_done_color
                text_color = self.text_done_color
            else:
                circle_color = self.circle_todo_color
                text_color = self.text_todo_color

            self.canvas.fill_style = circle_color
            self.canvas.begin_path()
            self.canvas.arc(x, r, r, 0, 2 * 3.14159)
            self.canvas.fill()

            self.canvas.fill_style = text_color
            self.canvas.font = f"{int(r * 1.5)}px Arial"
            self.canvas.text_align = "center"
            self.canvas.text_baseline = "middle"
            self.canvas.fill_text(str(i + 1), x, r)

            if dist_point_point(x, r, self.mouse_x, self.mouse_y) < r:
                self.canvas.stroke_style = text_color
                self.canvas.begin_path()
                self.canvas.arc(x, r, r * 0.8, 0, 2 * 3.14159)
                self.canvas.stroke()
                n_circle = i

            x += dx

        return n_circle

    def canvas_reset(self, **event_args):
        self.refresh()

    def canvas_show(self, **event_args):
        self.refresh()

    def canvas_mouse_leave(self, x, y, **event_args):
        self.mouse_x = -1
        self.mouse_y = -1
        self.refresh()

    def canvas_mouse_up(self, x, y, button, **event_args):
        self.mouse_x = x
        self.mouse_y = y
        n_circle = self.refresh()
        self.raise_event("click", n_circle=n_circle + 1)

    def canvas_mouse_move(self, x, y, **event_args):
        self.mouse_x = x
        self.mouse_y = y
        self.refresh()
