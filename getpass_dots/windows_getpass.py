import msvcrt
import sys

from typing import Optional, TextIO

from .abstract_getpass import AbstractGetpass
from .errors import GetpassError


class WindowsGetpass(AbstractGetpass):
    def __init__(
          self,
          input: Optional[TextIO] = None,
          output: Optional[TextIO] = None,
          strip_escapes: bool = True,
    ) -> None:
        if input is not None:
            raise ValueError("Setting input stream not supported on Windows")
        if output is None:
            output = sys.stderr
        super().__init__(
            input=input, output=output, strip_escapes=strip_escapes
        )

    def input_setup(self) -> None:
        """No setup needed on windows"""
        pass

    def print_prompt(self, prompt: str) -> None:
        if self.output == sys.__stderr__:
            # if output is default, write to TTY directly
            for c in prompt:
                msvcrt.putwch(c)
        else:
            super().print_prompt(prompt=prompt)

    def getchar(self) -> str:
        """
        Get characters from terminal using msvcrt.getwch().
        Skip escape sequences if self.strip_escapes is True.
        """

        if self.input is not sys.__stdin__:
            raise GetpassError(
                "Input other than stdin not supported on Windows"
            )

        while True:
            ch = msvcrt.getwch()

            # https://docs.python.org/3/library/msvcrt.html
            # If the pressed key was a special function key, this will return
            # '\000' or '\xe0'; the next call will return the keycode.

            if not self.strip_escapes:
                return ch

            if ch == "\x00" or ch == "\xe0":
                # discard next keycode, part of escape sequence
                msvcrt.getch()
            else:
                return ch
