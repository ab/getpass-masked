import io
import os
import sys
import termios
import tty

from .abstract_getpass import AbstractGetpass
from .errors import NoTTYError


class UnixGetpass(AbstractGetpass):
    def input_setup(self) -> None:
        fd: int

        if self.input:
            # user-specified input stream
            if not self.input.isatty():
                raise NoTTYError("Provided input argument is not a TTY")

            fd = self.input.fileno()
            self.input_handle = self.input

        else:
            # input stream not specified

            try:
                # Always try reading and writing directly on the tty first.
                fd = os.open("/dev/tty", os.O_RDWR | os.O_NOCTTY)
                tty = io.FileIO(fd, "w+")
                self.stack.enter_context(tty)
                self.input_handle = io.TextIOWrapper(tty, newline="\n")
                self.stack.enter_context(self.input_handle)

                if self.output is None:
                    self.output = self.input_handle

            except OSError:
                # If that fails, see if stdin can be controlled.
                # This case may happen if /dev/tty is inaccessible but we can
                # still access the TTY via sys.stdin.
                self.stack.close()
                fd = sys.stdin.fileno()
                self.input_handle = sys.stdin

                if not self.input_handle.isatty():
                    raise NoTTYError("sys.stdin is not a TTY")

        # disable echo on input TTY
        self.disable_echo(fd=fd)

        if self.output is None:
            self.output = sys.stderr

    def disable_echo(self, fd: int) -> None:
        """
        Disable echo on the given TTY file descriptor.
        Add a callback to the self.stack ExitStack to restore the original
        TTY settings.
        """
        # save copy
        old = termios.tcgetattr(fd)

        # dump unread input, add TCSASOFT (BSD-only)
        tcsetattr_flags = termios.TCSAFLUSH
        if hasattr(termios, 'TCSASOFT'):
            tcsetattr_flags |= termios.TCSASOFT

        # set TTY to raw mode, disabling echo
        tty.setraw(fd=fd, when=tcsetattr_flags)

        # add callback to restore settings to our exit stack
        self.stack.callback(termios.tcsetattr, fd, tcsetattr_flags, old)

    def getchar(self) -> str:
        """
        Read the next character from stdin, optionally skipping past any ANSI
        escape sequences.
        """
        def getch() -> str:
            # termios.tcflush(self.input_handle.fileno(), termios.TCIFLUSH)
            return self.input_handle.read(1)

        ch: str = getch()

        while True:
            # if we're not stripping escapes out, then return anything raw
            if not self.strip_escapes:
                return ch

            # All C0 control codes we return as is

            # When strip_escapes is set, we remove ANSI escape sequences
            # starting with ^[ (ESC)

            # if not ESC, return normal character
            if ch != "\x1B":
                return ch

            # read next char after ESC
            ch = getch()

            # Determine whether the next char is part of the escape sequence.
            if ch == "[":
                # This is a multi-byte CSI (Control Sequence Introducer)
                # sequence

                # Read next char
                ch = getch()

                # consume any parameter bytes in 0x30-0x3F [0-?]
                while "\x30" <= ch <= "\x3F":
                    ch = getch()

                # consume any intermediate bytes in 0x20-0x2F [ -/]
                while "\x20" <= ch <= "\x2F":
                    ch = getch()

                if "\x40" <= ch <= "\x7E":
                    # correct final byte, continue with next char
                    ch = getch()
                    continue
                else:
                    # invalid final byte... invalid escape sequence
                    raise ValueError("Invalid ANSI CSI escape sequence")

            elif "\x40" <= ch <= "\x5F":
                # This is a C1 Fe escape sequence of two bytes, discard char
                # and continue after next char
                ch = getch()
                continue

            else:
                # Char following ESC is not part of an escape sequence, retry
                # loop and process as standalone character
                continue

            raise NotImplementedError("notreached")
