import warnings

from toga.handlers import wrapped_handler

from .base import Widget


class Slider(Widget):
    """ Slider widget, displays a range of values

    Args:
        id: An identifier for this widget.
        style (:obj:`Style`):
        default (float): Default value of the slider
        range (``tuple``): Min and max values of the slider in this form (min, max).
        tick_count (``int``): How many ticks in range. if None, slider is continuous.
        on_change (``callable``): The handler to invoke when the slider value changes.
        on_focus_gain (:obj:`callable`): Function to execute when get focused.
        on_focus_loss (:obj:`callable`): Function to execute when lose focus.
        enabled (bool): Whether user interaction is possible or not.
        factory (:obj:`module`): A python module that is capable to return a
            implementation of this class with the same name. (optional & normally not needed)
    """
    def __init__(
        self,
        id=None,
        style=None,
        default=None,
        range=None,
        tick_count=None,
        on_change=None,
        on_focus_gain=None,
        on_focus_loss=None,
        on_slide=None,
        enabled=True,
        factory=None
    ):
        super().__init__(id=id, style=style, factory=factory)

        # Needed for _impl initialization
        self._tick_count = None
        self._on_change = None

        self._impl = self.factory.Slider(interface=self)

        self.range = range
        self.tick_count = tick_count

        # IMPORTANT NOTE: Setting value before on_change in order to not
        # call it in constructor. Please do not move it from here.
        self.value = default

        if on_slide:
            self.on_slide = on_slide
        else:
            self.on_change = on_change
        self.enabled = enabled
        self.on_focus_loss = on_focus_loss
        self.on_focus_gain = on_focus_gain

    MIN_WIDTH = 100

    @property
    def value(self):
        """ Current slider value.

        Returns:
            The current slider value as a ``float``.

        Raises:
            ValueError: If the new value is not in the range of min and max.
        """
        return self._impl.get_value()

    @value.setter
    def value(self, value):
        if value is None:
            final = (self.min + self.max) / 2
        elif self.min <= value <= self.max:
            final = value
        else:
            raise ValueError(
                'Slider value ({}) is not in range ({}-{})'.format(
                    value, self.min, self.max)
            )
        self._impl.set_value(final)
        if self.on_change:
            self.on_change(self)

    @property
    def range(self):
        """ Range composed of min and max slider value.

        Returns:
            Returns the range in a ``tuple`` like this (min, max)
        """
        return self.min, self.max

    @range.setter
    def range(self, range):
        default_range = (0.0, 1.0)
        _min, _max = default_range if range is None else range
        if _min > _max or _min == _max:
            raise ValueError('Range min value has to be smaller than max value.')
        self._min = _min
        self._max = _max
        self._impl.set_range((_min, _max))

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    @property
    def tick_count(self):
        return self._tick_count

    @tick_count.setter
    def tick_count(self, tick_count):
        self._tick_count = tick_count
        self._impl.set_tick_count(tick_count)

    @property
    def tick_step(self):
        if self.tick_count is None:
            return None
        return (self.max - self.min) / (self.tick_count - 1)

    @property
    def tick_value(self):
        """The value of the slider, measured in ticks.

        If tick count is not None, a value between 1 and tick count.
        Otherwise, None.
        """
        if self.tick_count is not None and self.value is not None:
            return round((self.value - self.min) / self.tick_step) + 1
        else:
            return None

    @tick_value.setter
    def tick_value(self, tick_value):
        if tick_value is not None and self.tick_count is None:
            raise ValueError("Cannot set tick value when tick count is None")
        if tick_value is not None:
            self.value = self.min + (tick_value - 1) * self.tick_step

    @property
    def on_change(self):
        """ The function for when the value of the slider is changed

        Returns:
            The ``callable`` that is executed when the value changes.
        """
        return self._on_change

    @on_change.setter
    def on_change(self, handler):
        self._on_change = wrapped_handler(self, handler)
        self._impl.set_on_change(self._on_change)

    @property
    def on_slide(self):
        """ The function for when the value of the slider is changed

        **DEPRECATED: renamed as on_change**

        Returns:
            The ``callable`` that is executed on slide.
        """
        warnings.warn("Slider.on_slide has been renamed Slider.on_change", DeprecationWarning)
        return self._on_change

    @on_slide.setter
    def on_slide(self, handler):
        warnings.warn("Slider.on_slide has been renamed Slider.on_change", DeprecationWarning)
        self.on_change = handler
