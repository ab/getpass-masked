"""
Prompt the user for a password and print the result on stdout.

The password prompt will be printed to the TTY or to stderr. Input is read from
stdin and terminated by a newline. The result is written verbatim with no
trailing newline to stdout.
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

    opts, args = p.parse_args()

    if args:
        prompt = " ".join(args)
    else:
        prompt = "Password: "

    out_stream = sys.stdout

    try:
        pw = getpass_dots(prompt=prompt, mask=opts.mask)
    except EOFError:
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(2)

    out_stream.write(pw)
    if opts.newline:
        out_stream.write("\n")


if __name__ == "__main__":
    main()
