# getpass-dots

[![PyPI](https://img.shields.io/pypi/v/getpass-dots.svg)](https://pypi.org/project/getpass-dots/)
[![Changelog](https://img.shields.io/github/v/release/ab/getpass-dots?include_prereleases&label=changelog)](https://github.com/ab/getpass-dots/releases)
[![Tests](https://github.com/ab/getpass-dots/workflows/Test/badge.svg)](https://github.com/ab/getpass-dots/actions?query=workflow%3ATest)
[![Codecov](https://img.shields.io/codecov/c/github/ab/getpass-dots)](https://app.codecov.io/github/ab/getpass-dots)
[![License](https://img.shields.io/github/license/ab/getpass-dots)](https://github.com/ab/getpass-dots/blob/main/LICENSE)

`getpass-dots` provides a way to prompt for passwords that echoes a dot (•/\*)
to the terminal for each key entered.

This is similar to the built-in `getpass` module, but it is slightly more
user-friendly because you can see how many letters you've typed and delete
typos with backspace as needed.

Don't use this module if you care about revealing the password length to someone who can see your screen. (Most modern password prompts believe this doesn't matter.)

## Installation

As a library, add `getpass_dots` to your dependencies.

```
pip install getpass_dots
```

For use as a standalone CLI for the `askpass` binary, use `pipx`:

```
pipx install getpass_dots

askpass
```

## Library usage

`getpass_dots.getpass_dots()` is a drop-in replacement for `getpass.getpass()`.

```py
from getpass_dots import getpass_dots

# prompt for secret
secret = getpass_dots(prompt="Your secret: ")
```

Full usage:

```
Signature:

    getpass_dots.getpass_dots(
        prompt: str = 'Password: ',
        mask: str = '•',
        input: Optional[TextIO] = None,
        output: Optional[TextIO] = None,
    ) -> str


Docstring:

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
```


## `askpass` script

When installed standalone, getpass-dots provides the `askpass` script, which
can be run from a terminal to prompt for a password and print the result to
stdout.

```
$ askpass
Password: •••
foo
```

Full help text:

```
$ askpass -h
Usage: askpass [OPTIONS] [PROMPT]
Prompt the user for a password and print the result on stdout.

The password prompt will be printed to the TTY or to stderr. Input is read from
the TTY or stdin and terminated by a newline. The result is written verbatim
with no trailing newline to stdout.

Options:
  -h, --help            show this help message and exit
  -n, --newline         print trailing newline
  -m CHAR, --mask=CHAR  Use CHAR as mask character (empty to disable)
```

## Prior art

Other similar packages include:

* https://github.com/FuturisticGoo/maskpass -- uses `pynput` dependency
* https://github.com/secursive/getpass_asterisk
