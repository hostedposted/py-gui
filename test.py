# from pygui import Window, Elements


# window = Window(title="Hello World")


# @window.frame("Hello World", width=700, height=450)
# def test(elements: Elements):
#     elements.text(
#         "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
#         text_color=elements.state.get("color", 0x008080),
#     )

#     @elements.button("Click me")
#     def click_me():
#         print("Clicked")

#     selected = elements.checkbox("Check me", True)
#     elements.text(f"Checked: {selected}")

#     color = elements.color_picker("Pick a color", 0x008080, key="color")
#     elements.text(f"Color: {color}", text_color=color)

#     integer = elements.input_int("Enter a number (2 to 8)", 5, 2, 8)
#     elements.text(f"You picked: {integer}")

#     text = elements.input_text("Enter a text", "Hello World", max_length=15)
#     elements.text(f"You typed: {text}")

# @window.menu("File", "Quit", keys=["Ctrl", "Q"])
# def quit_program():
#     exit(0)

# window.start()

import pygui

window = pygui.Window("Hello World")

@window.frame("Hello World", width=700, height=450)
def hello_world(elements: pygui.Elements):
    value = elements.input_int("What is your favorite number?", 7, key="favorite")
    @elements.button("Add 2")
    def add_2():
        elements.state["favorite"] = value + 2

window.start()
