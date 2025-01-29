import contextlib
import itertools
from io import StringIO
from unittest.mock import Mock
from typing import Any, NamedTuple

import pytest

from getpass_dots.unix_getpass import UnixGetpass


class Case(NamedTuple):
    label: str
    input: Any
    expected: Any = None
    raises: Any = None


def fake_tty(initial_value: str = "", fd_counter=itertools.count(1000)) -> Mock:
    sio = StringIO(initial_value=initial_value)
    m = Mock(wraps=sio)
    m.isatty = lambda: True

    # give this fake_tty a unique fileno (starts at 1000 by default)
    fileno = next(fd_counter)
    m.fileno = lambda: fileno

    return m


@pytest.mark.parametrize(
    "case",
    [
        Case("simple test", "foo bar", ["f", "o", "o", " ", "b", "a", "r"]),
        Case("ansi color", "c: \033[34;1mblue\033[m", list("c: blue")),
        Case("C0 codes passed through", "\x03\x0d\x0a\x09", list("\x03\r\n\t")),
        Case("arrows", "foo\033[A\033[B\033[D\033[Dbar", list("foobar")),
        Case(
            "invalid",
            "foo\033[\x80bar",
            list("foo"),
            pytest.raises(ValueError, match="Invalid ANSI"),
        ),
        Case(
            "function keys F1-F4",
            "F1-F4: OPOQOROS$",
            list("F1-F4: $"),
        ),
        Case(
            "function keys F5-F12",
            "F5-F12: [15~[17~[18~[19~[20~[O[23~[24~.",
            list("F5-F12: ."),
        ),
    ],
    ids=lambda tc: tc.label,
)
def test_getchar(mocker, case):
    input = case.input
    expected = case.expected
    raises = case.raises

    intty = fake_tty(input)
    outtty = fake_tty()

    gp = UnixGetpass(input=intty, output=outtty)
    mocker.patch.object(gp, "disable_echo", lambda fd: None)

    gp.input_setup()
    assert gp.strip_escapes is True

    output = []

    if raises:
        context = raises
    else:
        context = contextlib.nullcontext()

    with context:
        while res := gp.getchar():
            output.append(res)

    assert output == expected


@pytest.mark.parametrize(
    "case",
    [
        Case("simple test", "foo bar"),
        Case("ansi color", "c: \033[34;1mblue\033[m"),
        Case("C0 codes passed through", "\x03\x0d\x0a\x09"),
        Case("arrows", "foo\033[A\033[B\033[D\033[Dbar"),
        Case("invalid", "foo\033[\x80bar"),
        Case(
            "function keys F1-F4",
            "F1-F4: OPOQOROS$",
        ),
        Case(
            "function keys F5-F12",
            "F5-F12: [15~[17~[18~[19~[20~[O[23~[24~.",
        ),
    ],
    ids=lambda tc: tc.label,
)
def test_getchar_raw(mocker, case):
    intty = fake_tty(case.input)
    outtty = fake_tty()

    gp = UnixGetpass(input=intty, output=outtty, strip_escapes=False)
    mocker.patch.object(gp, "disable_echo", lambda fd: None)

    gp.input_setup()
    assert gp.strip_escapes is False

    output = []

    while res := gp.getchar():
        output.append(res)

    expected = list(case.input)

    assert output == expected
