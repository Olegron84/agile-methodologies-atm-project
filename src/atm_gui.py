import tkinter as tk

from atm_controller import ATMController
from atm_types import Shortcut

BACKGROUND = "#2b2f36"
SCREEN_BG = "#0b3d2e"
SCREEN_FG = "#b6f5c9"
KEY_BG = "#d9d9d9"
CLEAR_BG = "#f2c94c"
ENTER_BG = "#6fcf97"
SIDE_BG = "#9aa5b1"

SCREEN_FONT = ("Courier", 16, "bold")
KEY_FONT = ("Helvetica", 16, "bold")
SIDE_FONT = ("Helvetica", 12, "bold")

KEYPAD_ROWS = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    [".", "0", ""],
]


class ATMWindow:
    """Tkinter window with the ATM screen, side buttons and keypad."""

    def __init__(self, root: tk.Tk, atm: ATMController):
        self.root = root
        self.atm = atm
        self.side_buttons = {}

        root.title("ATM")
        root.configure(bg=BACKGROUND, padx=20, pady=20)
        root.resizable(False, False)

        self.build_screen()
        self.build_keypad()
        self.bind_keyboard()
        self.refresh()

    def build_screen(self) -> None:
        """Display in the middle with shortcut buttons A-C on the right."""
        frame = tk.Frame(self.root, bg=BACKGROUND)
        frame.pack(pady=(0, 20))

        self.display = tk.Label(
            frame, width=32, height=8, bg=SCREEN_BG, fg=SCREEN_FG,
            font=SCREEN_FONT, justify="center", wraplength=380,
            relief="sunken", bd=6,
        )
        self.display.grid(row=0, column=0, rowspan=len(Shortcut), padx=(0, 10))

        for row, key in enumerate(Shortcut):
            button = tk.Button(
                frame, width=10, height=2, font=SIDE_FONT, bg=SIDE_BG,
                highlightbackground=BACKGROUND,
                command=lambda key=key: self.press(self.atm.handle_shortcut, key),
            )
            button.grid(row=row, column=1, pady=4, sticky="ns")
            self.side_buttons[key] = button

    def build_keypad(self) -> None:
        """Digit keys 0-9 and '.', with Clear and Enter on the right."""
        frame = tk.Frame(self.root, bg=BACKGROUND)
        frame.pack()

        for row, keys in enumerate(KEYPAD_ROWS):
            for column, key in enumerate(keys):
                if not key:
                    continue
                self.make_key(frame, key, KEY_BG,
                              lambda key=key: self.press(self.atm.handle_digit, key),
                              row, column)

        self.make_key(frame, "Clear", CLEAR_BG,
                      lambda: self.press(self.atm.handle_clear), 0, 3)
        self.make_key(frame, "Enter", ENTER_BG,
                      lambda: self.press(self.atm.handle_enter), 1, 3)

    def make_key(self, frame, text, color, command, row, column) -> None:
        button = tk.Button(
            frame, text=text, width=5, height=2, font=KEY_FONT, bg=color,
            highlightbackground=BACKGROUND, command=command,
        )
        button.grid(row=row, column=column, padx=4, pady=4)

    def bind_keyboard(self) -> None:
        """Let the computer keyboard work like the ATM keypad."""
        for key in "0123456789":
            self.root.bind(key, lambda event, key=key: self.press(self.atm.handle_digit, key))
        self.root.bind(".", lambda event: self.press(self.atm.handle_digit, "."))
        self.root.bind("<Return>", lambda event: self.press(self.atm.handle_enter))
        self.root.bind("<BackSpace>", lambda event: self.press(self.atm.handle_clear))
        self.root.bind("<Escape>", lambda event: self.press(self.atm.handle_clear))
        for key in Shortcut:
            self.root.bind(key.lower(), lambda event, key=key: self.press(self.atm.handle_shortcut, key))

    def press(self, handler, *args) -> None:
        """Call a controller action, then redraw the screen."""
        handler(*args)
        self.refresh()

    def refresh(self) -> None:
        """Show the current display text and shortcut labels."""
        self.display.config(text=self.atm.get_display_text())

        labels = self.atm.get_shortcut_labels()
        for key, button in self.side_buttons.items():
            label = labels.get(key, "")
            if label:
                button.config(text=f"{key}  {label}", state="normal")
            else:
                button.config(text=str(key), state="disabled")


def main() -> None:
    root = tk.Tk()
    ATMWindow(root, ATMController())
    root.mainloop()


if __name__ == "__main__":
    main()
