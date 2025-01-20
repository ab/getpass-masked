from getpass_dots import Getpass, getpass_dots
from getpass_dots.abstract_getpass import AbstractGetpass


def test_getpass_class():
    assert issubclass(Getpass, AbstractGetpass)
