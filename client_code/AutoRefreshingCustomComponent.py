from anvil.designer import in_designer
import anvil


class _PropertyWrapper:
    """
    Descriptor that wraps a CustomComponentProperty,
    and defers refreshing via a debounced Timer
    """
    def __init__(self, component_property, prop_name):
        print(f'_PropertyWrapper({component_property}, {prop_name})')
        self.property = component_property
        self.prop_name = prop_name

    def __get__(self, obj, obj_type):
        print(f'_PropertyWrapper.__get__({obj}, {obj_type})')
        return self.property.__get__(obj, obj_type)

    def __set__(self, obj, value):
        print(f'_PropertyWrapper.__set__({obj}, {value})')
        old_value = self.property.__get__(obj, type(obj))
        self.property.__set__(obj, value)

        if self.prop_name in obj.__class__.auto_refresh_props and value != old_value:
            obj._schedule_refresh()


class AutoRefreshingCustomComponent:
    """
      1. Subclass this mixin alongside the _Template class
      2. At the class level of the custom component:
           AutoRefreshingCustomComponent.auto_refresh_on_property_change(['prop1', 'prop2'], 0.2)
         listing which property names should cause a refresh
      3. Implement a `refresh()` method on the custom component (called after the 0.2s debounce)
    """
    auto_refresh_props = set()
    delay = 0.2

    @classmethod
    def auto_refresh_on_property_change(cls, prop_names, delay=0.2):
        print(f'AutoRefreshingCustomComponent.auto_refresh_on_property_change({prop_names}, {delay})')
        cls.auto_refresh_props = set(prop_names)
        cls.delay = delay

    def __init_subclass__(cls, **kwargs):
        print(f'AutoRefreshingCustomComponent.__init_subclass__({kwargs})')
        super().__init_subclass__(**kwargs)
        if not in_designer:
            return

        for prop_name in dir(cls):
            prop_value = getattr(cls, prop_name)
            if isinstance(prop_value, anvil.CustomComponentProperty):
                setattr(cls, prop_name, _PropertyWrapper(prop_value, prop_name))

    def _schedule_refresh(self):
        print(f'AutoRefreshingCustomComponent._schedule_refresh')
        if not hasattr(self, "_debounce_timer"):
            t = anvil.Timer()
            t.interval = 0  
            t.set_event_handler("tick", self._on_debounce_timer_tick)
            self._debounce_timer = t
            self.add_component(t)

        self._debounce_timer.interval = self.delay
        self._debounce_timer.enabled = True

    def _on_debounce_timer_tick(self, **event_args):
        print(f'AutoRefreshingCustomComponent._on_debounce_timer_tick({event_args})')
        self._debounce_timer.enabled = False
        self._debounce_timer.interval = 0
        if callable(getattr(self, "refresh", None)):
            self.refresh()
