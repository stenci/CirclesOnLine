from anvil.designer import in_designer
import anvil


class _DebouncePropertyWrapper:
    """
    Descriptor that wraps a CustomComponentProperty,
    and defers refreshing via a debounced Timer.
    """

    def __init__(self, component_property, prop_name):
        self.property = component_property
        self.prop_name = prop_name

    def __get__(self, obj, obj_type):
        return self.property.__get__(obj, obj_type)

    def __set__(self, obj, value):
        old_value = self.property.__get__(obj, type(obj))
        self.property.__set__(obj, value)

        if self.prop_name in obj.__class__.auto_refresh_props and value != old_value:
            obj._schedule_debounced_refresh()


class DebouncedAutoRefreshingCustomComponent:
    """
    Mixin to allow "debounced" auto-refresh of your Custom Component.

    Usage:
      1) Subclass this mixin alongside your _Template class.
      2) At the *class level* of your custom component, call:
           DebouncedAutoRefreshingCustomComponent.auto_refresh_on_property_change([...])
         listing which property names should cause a refresh.
      3) Implement a `refresh()` method on your custom component (called after the 0.2s debounce).
    """

    # Which property names automatically trigger a (debounced) refresh?
    auto_refresh_props = set()

    @classmethod
    def auto_refresh_on_property_change(cls, prop_names):
        """Define which property names should auto-refresh (debounced) upon change."""
        cls.auto_refresh_props = set(prop_names)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not in_designer:
            # Only do the descriptor-wrapping in the designer environment
            return

        # For each CustomComponentProperty, wrap it with our debounced descriptor
        for prop_name in dir(cls):
            prop_value = getattr(cls, prop_name)
            if isinstance(prop_value, anvil.CustomComponentProperty):
                setattr(cls, prop_name, _DebouncePropertyWrapper(prop_value, prop_name))

    def _schedule_debounced_refresh(self):
        """
        Called when an auto-refresh property changes. Resets the Timer to 0.2s.
        After 0.2s of no new changes, the Timer calls self.refresh().
        """
        # Make sure we have a Timer
        if not hasattr(self, "_debounce_timer"):
            # Create a Timer on-the-fly and add it as a child
            t = anvil.Timer()
            t.interval = 0  # Start disabled
            t.visible = False
            t.set_event_handler("tick", self._on_debounce_timer_tick)
            self._debounce_timer = t

            # If your custom component is a Container (has .add_component),
            # then we can add the Timer to it:
            self.add_component(t)

        # Each time we get a property change, re-arm the Timer to 0.2s
        self._debounce_timer.interval = 0.2
        self._debounce_timer.enabled = True

    def _on_debounce_timer_tick(self, **event_args):
        """
        Called once the Timer reaches 0.2s with no further property changes.
        Disable the Timer, then call self.refresh().
        """
        self._debounce_timer.enabled = False
        self._debounce_timer.interval = 0
        if callable(getattr(self, "refresh", None)):
            self.refresh()
