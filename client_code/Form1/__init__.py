from ._anvil_designer import Form1Template


class Form1(Form1Template):
    def __init__(self, **properties):
        self.init_components(**properties)

    def update_circles(self, **event_args):
        self.circles_on_line_1.n_circles_tot = self.number_of_circles.text
        self.circles_on_line_1.n_circles_done = self.number_done.text

    def form_show(self, **event_args):
        self.update_circles()
