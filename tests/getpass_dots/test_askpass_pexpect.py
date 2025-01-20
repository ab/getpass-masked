from subprocess import check_output

import pexpect

from getpass_dots import askpass


def test_askpass_pexpect():
    """
    Test that we can call askpass with a TTY from pexpect.
    Verify that echo is turned off and the mask and password are printed as
    expected.
    """
    p = pexpect.spawn("askpass", args=[], timeout=3, encoding="utf-8")

    # wait for prompt
    p.expect("Password: ")

    # check that askpass turned off tty echo
    assert p.getecho() is False

    password = "mysecret"

    p.sendline(password)

    out = p.read()

    lines = out.split("\r\n")
    assert lines

    # output should be echoed mask and then password
    # right now we don't differentiate between stdout/stderr
    assert lines[0] == "•" * len(password)
    assert lines[1] == password
    assert len(lines) == 2

    assert p.wait() == 0

    # check that echo is back on after process exits
    assert p.getecho() is True


def test_askpass_mask():
    """
    Test custom mask character via pexpect
    """
    p = pexpect.spawn("askpass", args=["--mask", "X"], timeout=3, encoding="utf-8")

    # wait for prompt
    p.expect("Password: ")

    # check that askpass turned off tty echo
    assert p.getecho() is False

    password = "the pass word"

    p.sendline(password)

    out = p.read()

    lines = out.split("\r\n")
    assert lines

    # output should be echoed mask and then password
    # right now we don't differentiate between stdout/stderr
    assert lines[0] == "X" * len(password)
    assert lines[1] == password
    assert len(lines) == 2

    assert p.wait() == 0

    # check that echo is back on after process exits
    assert p.getecho() is True


def test_askpass_mock(mocker, capsys):
    """
    Test only CLI glue with mocked out getpass_dots function
    """
    mocker.patch("sys.argv", ["askpass"])
    gp = mocker.patch.object(askpass, "getpass_dots")
    gp.return_value = "pw_output"

    askpass.main()

    out, err = capsys.readouterr()

    assert out == "pw_output"


def test_askpass_mock_nl(mocker, capsys):
    """
    Test only CLI, verify that newline option works
    """
    mocker.patch("sys.argv", ["askpass", "-n"])
    gp = mocker.patch.object(askpass, "getpass_dots")
    gp.return_value = "pw_output"

    askpass.main()

    out, err = capsys.readouterr()

    assert out == "pw_output\n"
