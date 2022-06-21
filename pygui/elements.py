"""
Elements for the gui to display.
"""
import collections.abc
import math
import warnings
from typing import Optional, Union

import imgui

WRAPPING_PERCENTAGE = 0.9


def hex_to_rgb(hex_value: int) -> tuple:
    """
    Convert's hex to RGB.

    Parameters
    ----------
    hex_value : int
        The hex value. This should be an integer. Example: ``0xFF0000``

    Returns
    -------
    tuple
        The hex value as an RGB value.
    """
    return (hex_value >> 16) & 0xFF, (hex_value >> 8) & 0xFF, hex_value & 0xFF


def clamp(number: int, minimum: int, maximum: int):
    """
    Clamp a number between the minimum and maximum.

    Parameters
    ----------
    number : int
        The number to clamp.
    minimum : int
        The minimum of the range. This number is included in the range.
    maximum : int
        The maximum of the range. This number is included in the range.

    Returns
    -------
    int
        The clamped value.
    """
    return max(minimum, min(number, maximum))


class State(collections.abc.MutableMapping, dict):  # type: ignore
    """
    The state object.
    """

    convert: bool = True

    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        if self.convert and isinstance(value, tuple) and len(value) in (3, 4):
            return tuple(round(i * 255) for i in value[:3]) + (
                (value[3],) if len(value) == 4 else ()
            )

        return value

    def __setitem__(self, key, value):
        if self.convert and isinstance(value, tuple) and len(value) in (3, 4):
            value = tuple(i / 255 for i in value[:3]) + (
                (value[3],) if len(value) == 4 else ()
            )
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)

    def __contains__(self, x):
        return dict.__contains__(self, x)


class Elements:
    """
    A class full of elements that can be added to the gui.
    """

    state: State

    def __init__(self, state: State) -> None:
        self.state = state

    def text(
        self,
        text: str,
        text_color: Union[tuple, int] = (255, 255, 255, 1),
        center: bool = False,
        wrap_text: bool = True,
    ) -> None:
        """
        Add's a text element to the GUI.

        Parameters
        ----------
        text : str
            The text to add.
        text_color : Union[tuple, int], optional
            The color of the text, by default (255, 255, 255, 1)
        center : bool, optional
            Wether or not the text should be centered, by default False
        wrap_text : bool, optional
            Wether or not the text should be wrapped, by default True
        """
        if center and wrap_text:
            warnings.warn(
                "Cannot center text and wrap text at the same time (yet). Center will be set to false."
            )
            center = False
        if isinstance(text_color, int):
            text_color = hex_to_rgb(text_color)
        if isinstance(text_color, tuple):
            if len(text_color) == 3:
                text_color = text_color + (1,)
            imgui.push_style_color(
                imgui.COLOR_TEXT,
                text_color[0] / 255,
                text_color[1] / 255,
                text_color[2] / 255,
                text_color[3],
            )
        if center:
            window_width = imgui.get_window_width()
            text_width = imgui.calc_text_size(text).x

            imgui.set_cursor_pos_x((window_width - text_width) / 2)
        if wrap_text:
            imgui.push_text_wrap_pos(imgui.get_window_width() * WRAPPING_PERCENTAGE)
        imgui.text(text)
        if isinstance(text_color, tuple):
            imgui.pop_style_color()
        if wrap_text:
            imgui.pop_text_wrap_pos()

    def button(
        self,
        text: str,
        text_color: Union[tuple, int] = (255, 255, 255, 1),
        wrap_text: bool = True,
        key: Optional[str] = None
    ):
        """
        Create a button element.

        Parameters
        ----------
        text : str
            The text to be displayed on the button.
        text_color : Union[tuple, int], optional
            The color of the text, either RGB or HEX, by default (255, 255, 255, 1)
        wrap_text : bool, optional
            Wether or not the text should be wrapped to fit, by default True
        key : str, optional
            A key for the color picker. This can be used for accessing the state of the element before it is added to the frame, by default None


        Returns
        -------
        Callable
            A decorator for handling the click event.
        """
        if wrap_text:
            imgui.push_text_wrap_pos(imgui.get_window_width() * WRAPPING_PERCENTAGE)
        if isinstance(text_color, int):
            text_color = hex_to_rgb(text_color)
        if isinstance(text_color, tuple):
            if len(text_color) == 3:
                text_color = text_color + (1,)
            imgui.push_style_color(
                imgui.COLOR_TEXT,
                text_color[0] / 255,
                text_color[1] / 255,
                text_color[2] / 255,
                text_color[3],
            )
        clicked = imgui.button(text)
        if wrap_text:
            imgui.pop_text_wrap_pos()
        if isinstance(text_color, tuple):
            imgui.pop_style_color()

        def button_handler(func):
            if clicked:
                self.state[key or text] = imgui.get_time()
                func()

        return button_handler

    def button_event(self, key: str, time_limit: int = 10):
        """
        After a button is clicked call the passed function every `time_limit` seconds.

        Parameters
        ----------
        key : str
            The key of the button.
        time_limit : int, optional
            How long this should be called after the button's click, by default 10

        Returns
        -------
        Callable
            A decorator for handling element's that only get rendered after a button click.
        """
        def handler(func):
            if imgui.get_time() - self.state.get(key, -math.inf) < time_limit:
                func()

        return handler

    def checkbox(
        self, label: str, default_value: bool, key: Optional[str] = None
    ) -> bool:
        """
        Create a checkbox.

        Parameters
        ----------
        label : str
            Text to appear after the checkbox.
        default_value : bool
            The default value of the check box.
        key : Optional[str], optional
            A key for the checkbox. This can be used for accessing the state of the element before it is added to the frame, by default None

        Returns
        -------
        bool
            If the checkbox is checked.
        """
        changed, value = imgui.checkbox(
            " " + label,
            self.state.get(
                key or label, default_value
            ),  # Adding a space to the label make's it look better
        )
        if changed:
            self.state[label] = value
        return value

    def color_picker(
        self,
        label: str,
        default_value: Union[int, tuple],
        alpha: bool = False,
        key: Optional[str] = None,
    ) -> tuple:
        """
        Create's a color picker.

        Parameters
        ----------
        label : str
            Text that will be displayed after the color picker.
        default_value : Union[int, tuple]
            The default color of the color picker. Can be a HEX or RGB value.
        alpha : bool, optional
            If alpha changing is allowed. If true then the default value can be RGBA, by default False
        key : str, optional
            A key for the color picker. This can be used for accessing the state of the element before it is added to the frame, by default None

        Returns
        -------
        tuple
            The currently selected color as an RGB or RGBA value. Vary's depending on wether alpha is set to true.
        """
        self.state.convert = False
        func = imgui.color_edit4 if alpha else imgui.color_edit3
        if isinstance(default_value, int):
            default_value = hex_to_rgb(default_value)
        if isinstance(default_value, tuple):
            old_default_value = default_value
            default_value = (
                default_value[0] / 255,
                default_value[1] / 255,
                default_value[2] / 255,
            )
            if alpha:
                if len(old_default_value) == 3:
                    default_value = default_value + (1,)
                else:
                    default_value = default_value + (old_default_value[3],)
        changed, value = func(
            " " + label,  # Adding a space to the label make's it look better
            *self.state.get(key or label, default_value),
        )
        if changed:
            self.state[key or label] = value
        rgb = (round(value[0] * 255), round(value[1] * 255), round(value[2] * 255))
        if alpha and len(value) == 4:
            rgb = rgb + (value[3],)
        self.state.convert = True
        return rgb

    def input_int(
        self,
        label: str,
        default_value: int = 0,
        minimum: int = -math.inf,
        maximum: int = math.inf,
        key: Optional[str] = None,
        wrap_text: bool = True,
    ):
        """
        Create an integer input.

        Parameters
        ----------
        label : str
            Text that will be displayed after the input.
        default_value : int, optional
            The default value, by default 0
        minimum : int, optional
            The minimum value that can be entered, by default -math.inf
        maximum : int, optional
            The maximum value that can be entered, by default math.inf
        key : Optional[str], optional
            A key for the input. This can be used for accessing the state of the element before it is added to the frame, by default None
        wrap_text : bool, optional
            Wether or not the text should be wrapped to fit, by default True

        Returns
        -------
        int
            The value entered.
        """
        if wrap_text:
            imgui.push_text_wrap_pos(imgui.get_window_width() * WRAPPING_PERCENTAGE)
        changed, value = imgui.input_int(
            " " + label, self.state.get(key or label, default_value)
        )  # Adding a space to the label make's it look better
        if wrap_text:
            imgui.pop_text_wrap_pos()
        if changed:
            value = clamp(value, minimum, maximum)
            self.state[key or label] = value
        return value

    def input_text(
        self,
        label: str,
        default_value: str = "",
        key: Optional[str] = None,
        wrap_text: bool = True,
        max_length: int = 255,
    ):
        """
        Create a text input.

        Parameters
        ----------
        label : str
            Text that will be displayed after the input.
        default_value : str, optional
            The default value, by default ""
        key : Optional[str], optional
            A key for the input. This can be used for accessing the state of the element before it is added to the frame, by default None
        wrap_text : bool, optional
            Wether or not the text should be wrapped to fit, by default True
        max_length : int, optional
            The maximum length of the entered text, by default 255

        Returns
        -------
        str
            The value entered.
        """
        if wrap_text:
            imgui.push_text_wrap_pos(imgui.get_window_width() * WRAPPING_PERCENTAGE)
        changed, value = imgui.input_text(
            " " + label, self.state.get(key or label, default_value), max_length + 1
        )  # Adding a space to the label make's it look better
        if wrap_text:
            imgui.pop_text_wrap_pos()
        if changed:
            self.state[key or label] = value
        return value
