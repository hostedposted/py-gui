"""
File for handling the window.
"""
import os
from typing import Callable, Dict, List, Literal, NamedTuple, Optional, Tuple, Type

import darkdetect
import glfw
import imgui
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
import pygui
from pygui.elements import Elements, State

KEY = Literal[
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "Ctrl",
    "Alt",
    "Shift",
]


class Frame(NamedTuple):
    """
    A Frame
    """

    func: Callable
    title: str
    width: int
    height: int
    position: Optional[Tuple[int, int]]


class Menu(NamedTuple):
    """
    A Menu
    """

    func: Callable
    title: str
    keys: Optional[List[KEY]]


Theme = Type[Literal["light", "dark", "auto"]]


class Window:
    """
    The window object.
    """

    title: str = "Window"
    width: int = 800
    height: int = 600
    frames: List[Frame] = []
    menus: Dict[str, List[Menu]] = {}
    state: State = State()
    theme: Theme

    def __init__(
        self,
        title: str,
        width: int = 800,
        height: int = 600,
        font: str = None,
        theme: Theme = "auto",
    ):
        self.title = title
        self.width = width
        self.height = height
        if font is None:
            font = os.path.join(
                os.path.dirname(pygui.__file__), "fonts", "Roboto-Regular.ttf"
            )
        self.font = font
        self.state = State()
        self.frames = []
        self.menus = {}
        self.theme = theme

    def start(self):
        """
        Start the window.

        Raises
        ------
        Exception
            If the OpenGL context or window could not be initialized.
        """
        imgui.create_context()

        if not glfw.init():
            raise Exception("Could not initialize OpenGL context")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

        window = glfw.create_window(self.width, self.height, self.title, None, None)
        glfw.make_context_current(window)

        if not window:
            glfw.terminate()
            raise Exception("Could not initialize Window")

        impl = GlfwRenderer(window)

        if (darkdetect.isLight() and self.theme == "auto") or self.theme == "light":
            imgui.style_colors_light()
        elif (darkdetect.isDark() and self.theme == "auto") or self.theme == "dark":
            imgui.style_colors_dark()

        io = imgui.get_io()
        font = io.fonts.add_font_from_file_ttf(self.font, 48)
        impl.refresh_font_texture()

        while not glfw.window_should_close(window):
            glfw.poll_events()
            impl.process_inputs()
            imgui.new_frame()

            gl.glClearColor(0.1, 0.1, 0.1, 1)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            imgui.push_font(font)

            if len(self.menus) > 0:
                for menu_items in self.menus.values():
                    for menu in menu_items:
                        if menu.keys is not None:
                            if all(
                                i == "Ctrl"
                                and io.key_ctrl
                                or i == "Alt"
                                and io.key_alt
                                or i == "Shift"
                                and io.key_shift
                                or len(i) == 1
                                and io.keys_down[getattr(glfw, f"KEY_{i.upper()}")]
                                for i in menu.keys
                            ):
                                menu.func()

                if imgui.begin_main_menu_bar():
                    for menu_name, menu_items in self.menus.items():
                        if imgui.begin_menu(menu_name, True):
                            for menu_item in menu_items:
                                subtext = " + ".join(menu_item.keys or [])
                                if imgui.menu_item(menu_item.title, subtext)[0]:
                                    menu_item.func()
                            imgui.end_menu()
                    imgui.end_main_menu_bar()

            for frame in self.frames:
                if frame.height and frame.width:
                    imgui.set_next_window_size(
                        frame.width, frame.height, imgui.FIRST_USE_EVER
                    )
                if len(frame.position or ()) == 2:
                    imgui.set_next_window_position(
                        frame.position[0], frame.position[1], imgui.FIRST_USE_EVER
                    )
                imgui.begin(frame.title)
                frame.func(Elements(self.state))
                imgui.end()
            imgui.pop_font()

            imgui.render()
            impl.render(imgui.get_draw_data())
            glfw.swap_buffers(window)

        impl.shutdown()
        glfw.terminate()

    def frame(self, title: str, width: int = None, height: int = None, position: Optional[Tuple[int, int]] = None):
        """
        Create a decorator to create a frame.

        Parameters
        ----------
        title : str
            The title of the frame
        width : int, optional
            The width of the frame, by default None
        height : int, optional
            The height of the frame, by default None

        Returns
        -------
        Callable
            The decorator.
        """
        return lambda func: self.frames.append(
            Frame(func=func, title=title, width=width, height=height, position=position)
        )

    def menu(self, category: str, title: str, keys: List[KEY] = None):
        """
        Create a decorator to create a menu.

        Parameters
        ----------
        category : str
            The category to put the button in.
        title : str
            The title of the button.
        keys : List[KEY], optional
            The keys to activate the menu, by default None

        Returns
        -------
        Callable
            The decorator.
        """
        return lambda func: self.menus.setdefault(category, []).append(
            Menu(func=func, title=title, keys=keys)
        )

    def __repr__(self) -> str:
        return f"Window(title={self.title!r}, width={self.width}, height={self.height})"
