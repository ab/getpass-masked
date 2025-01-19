import sys

import pytest

from getpass_dots import Getpass, getpass_dots
from getpass_dots.abstract_getpass import AbstractGetpass
from getpass_dots.unix_getpass import UnixGetpass


def test_getpass_class():
    assert issubclass(Getpass, AbstractGetpass)


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on Windows")
def test_getpass_unix():
    assert Getpass == UnixGetpass


@pytest.mark.skipif(sys.platform != "win32", reason="only runs on Windows")
def test_getpass_windows():
    from getpass_dots.windows_getpass import WindowsGetpass

    assert Getpass == WindowsGetpass
