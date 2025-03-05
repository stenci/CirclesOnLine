import anvil


class _PropertyWrapper:
    """
    Descriptor that wraps a CustomComponentProperty, and defers redrawing via a debounced Timer
    """

    def __init__(self, component_property, prop_name):
        self.property = component_property
        self.prop_name = prop_name

    def __get__(self, obj, obj_type):
        return self.property.__get__(obj, obj_type)

    def __set__(self, obj, value):
        old_value = self.property.__get__(obj, type(obj))
        self.property.__set__(obj, value)

        if value != old_value and self.prop_name not in obj.__class__.skip_properties:
            obj.schedule_redraw()


class AutoRedrawCustomComponent:
    """
    1. Subclass this mixin alongside the _Template class
    2. At the class level of the custom component list which properties should cause a redraw:
         AutoRedrawCustomComponent.skip_properties = {'prop1', 'prop2'}
         AutoRedrawCustomComponent.delay = 0.5
    3. Implement a `redraw()` method on the custom component (called after the 0.1s debounce)

    The custom component can call self.redraw() for an immediate redraw, for example inside
    mouse event handlers, or can call self.schedule_redraw() for a debounced redraw.
    """

    skip_properties = set()
    delay = 0.1

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        for prop_name in dir(cls):
            prop_value = getattr(cls, prop_name)
            if isinstance(prop_value, (anvil.CustomComponentProperty, property)):
                setattr(cls, prop_name, _PropertyWrapper(prop_value, prop_name))

    def schedule_redraw(self):
        if not hasattr(self, "_debounce_timer"):
            t = anvil.Timer()
            t.interval = 0
            t.set_event_handler("tick", self._on_debounce_timer_tick)
            self._debounce_timer = t
            self.add_component(t)

        self._debounce_timer.interval = max(self.delay, 0.001)

    def _on_debounce_timer_tick(self, **event_args):
        self._debounce_timer.interval = 0
        if callable(getattr(self, "redraw", None)):
            self.redraw()
