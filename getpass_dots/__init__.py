"""
Utilities to get a password, while echoing a mask asterisk for each char.

GetPassError - This exception is raised if we fail to set up the terminal to
               avoid echoing the password contents.

On Windows, the msvcrt module will be used.

This is a derived work that incorporates portions of CPython Lib/getpass.py,
used under the Python Software Foundation License Version 2.

Copyright (c) 2001-2024 Python Software Foundation
Copyright (c) 2024 Andy Brody
"""

import sys
from typing import Optional, TextIO

from .errors import GetpassError, NoTTYError


__all__ = [
    "GetpassError",
    "Getpass",
    "NoTTYError",
    "getpass_dots",
]


def getpass_dots(
    prompt: str = "Password: ",
    mask: str = "•",
    input: Optional[TextIO] = None,
    output: Optional[TextIO] = None,
) -> str:
    """
    Prompt for a password. Echo mask character for each input character.

    Args:
      prompt: Written on stream to ask for the input.  Default: 'Password: '
      input:  A readable file object to read the password from. Defaults to the
              tty. If no tty is available, defaults to sys.stdin. If this
              stream is not controllable as a tty, raise NoTTYError.
      output: A writable file object to display the prompt. Defaults to the
              tty. If no tty is available, defaults to sys.stderr.
      mask: The asterisk or dot character used to echo/mask each key.
    Returns:
      The password entered as a string, with no trailing newline.
    Raises:
      EOFError: If our input tty or stdin was closed.
      getpass_dots.NoTTYError: If we can't find a TTY for input.
      termios.error: If we encounter errors turning off TTY echo.

    Always restores terminal settings before returning.
    """

    with Getpass(input=input, output=output) as gp:
        return gp.read_input(prompt=prompt, mask=mask)


if sys.platform == "win32":
    # Windows
    from .windows_getpass import WindowsGetpass as Getpass

else:
    # macOS and Linux
    from .unix_getpass import UnixGetpass as Getpass
