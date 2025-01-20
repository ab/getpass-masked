"""
Prompt the user for a password and print the result on stdout.

The password prompt will be printed to the TTY or to stderr. Input is read from
the TTY or stdin and terminated by a newline. The result is written verbatim
with no trailing newline to stdout.
"""

import optparse
import sys

from . import getpass_dots


def main():
    p = optparse.OptionParser(
        usage="usage: %prog [OPTIONS] [PROMPT]" + __doc__.rstrip("\n")
    )
    p.add_option("-n", "--newline", help="print trailing newline", action="store_true")
    p.add_option(
        "-m",
        "--mask",
        metavar="CHAR",
        default="•",
        help="Use CHAR as mask character (empty to disable)",
    )
    p.add_option(
        "--no-dev-tty",
        dest="skip_dev_tty",
        action="store_true",
        help="Don't try to read/write directly to /dev/tty",
    )

    opts, args = p.parse_args()

    if args:
        prompt = " ".join(args)
    else:
        prompt = "Password: "

    out_stream = sys.stdout

    pwin = None
    pwout = None

    if opts.skip_dev_tty:
        pwin = sys.stdin
        pwout = sys.stderr

    try:
        pw = getpass_dots(prompt=prompt, mask=opts.mask, input=pwin, output=pwout)
    except EOFError:
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(2)

    out_stream.write(pw)
    if opts.newline:
        out_stream.write("\n")


if __name__ == "__main__":
    main()
