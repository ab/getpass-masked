from abc import abstractmethod
from contextlib import AbstractContextManager, ExitStack
from types import TracebackType
from typing import List, Optional, TextIO


class AbstractGetpass(AbstractContextManager):
    """
    Abstract class for common Getpass functions.

    This is a context manager class, meaning subclasses must also define
    __enter__() and __exit__() to handle setup of the TTY to disable echo.
    """

    def __init__(
        self,
        input: Optional[TextIO] = None,
        output: Optional[TextIO] = None,
        strip_escapes: bool = True,
    ) -> None:
        self.input = input
        self.output = output
        self.strip_escapes = strip_escapes
        self.inside_with = False

    def __enter__(self) -> "AbstractGetpass":
        self.inside_with = True
        self.stack = ExitStack()
        try:
            self.input_setup()
        except Exception:
            self.stack.close()
            raise
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.inside_with = False
        self.stack.close()

    @abstractmethod
    def input_setup(self) -> None:
        """
        Override this method to perform setup tasks like setting the TTY to raw
        mode with no echo.
        """
        raise NotImplementedError

    @abstractmethod
    def getchar(self) -> str:
        """
        Override this method to get a character from the input stream.
        """
        raise NotImplementedError

    def print_prompt(self, prompt: str) -> None:
        self.output.write(prompt)
        self.output.flush()

    def read_input(self, prompt: str = "Password: ", mask: str = "•") -> str:
        # verify that context manager was called
        if not self.inside_with:
            raise ValueError("Must be called inside 'with' block")

        # print prompt
        self.print_prompt(prompt=prompt)

        with self.stack:
            # get password
            return self._read_loop(mask=mask)

    def _read_loop(self, mask: str) -> str:
        """
        Read characters from self.input until we see a newline or ^D.
        Echo a mask character to self.output for each input char.

        Echo must already be disabled on the input stream.
        """

        password: List[str] = []

        while True:
            key = ord(self.getchar())

            # STX:3 (^C), FS:28 (^\)
            if key in (3, 28):
                # ^C or ^\ pressed
                raise KeyboardInterrupt

            # EOT:4, LF:10, CR:13
            elif key in (4, 10, 13):
                # ^D or enter pressed
                # Even on Unix, we use \r to return cursor to column 0
                self.output.write("\r\n")
                self.output.flush()
                return "".join(password)

            # ASCII BS:8 or DEL:127 are backspace.
            # Typically backspace sends DEL and ctrl+backspace sends BS.
            elif key in (8, 127):
                if len(password) > 0:
                    # Erase previous character
                    password = password[:-1]

                    if mask:
                        # Print \b to move cursor back, overwrite with space,
                        # then \b again
                        self.output.write("\b \b")
                        self.output.flush()

            elif 0 <= key <= 31:
                # Do nothing for unprintable characters.
                # We ignore arrow keys, home, end, etc.
                pass

            else:
                # Key is a normal char / part of the password
                # Echo the mask character
                char = chr(key)
                password.append(char)

                if mask:
                    self.output.write(mask)
                    self.output.flush()
