import argparse
import io
import sys

from snappy import snappy_formats as formats
from snappy import UncompressError

def main():
    """This method is what is run when invoking snappy via the commandline.
    Try python -m snappy --help
    """
    stdin = sys.stdin
    if hasattr(sys.stdin, "buffer"):
        stdin = sys.stdin.buffer
    stdout = sys.stdout
    if hasattr(sys.stdout, "buffer"):
        stdout = sys.stdout.buffer

    parser = argparse.ArgumentParser(
        description="Compress or decompress snappy archive"
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '-c',
        dest='compress',
        action='store_true',
        help='Compress'
    )
    group.add_argument(
        '-d',
        dest='decompress',
        action='store_true',
        help='Decompress'
    )

    parser.add_argument(
        '-t',
        dest='target_format',
        default=formats.DEFAULT_FORMAT,
        choices=formats.ALL_SUPPORTED_FORMATS,
        help=(
            'Target format, default is "{}"'.format(formats.DEFAULT_FORMAT)
        )
    )

    parser.add_argument(
        'infile',
        nargs='?',
        type=argparse.FileType(mode='rb'),
        default=stdin,
        help="Input file (or stdin)"
    )
    parser.add_argument(
        'outfile',
        nargs='?',
        type=argparse.FileType(mode='wb'),
        default=stdout,
        help="Output file (or stdout)"
    )

    args = parser.parse_args()

    # workaround for https://bugs.python.org/issue14156
    if isinstance(args.infile, io.TextIOWrapper):
        args.infile = stdin
    if isinstance(args.outfile, io.TextIOWrapper):
        args.outfile = stdout

    additional_args = {}
    if args.compress:
        method = formats.get_compress_function(args.target_format)
    else:
        try:
            method, read_chunk = formats.get_decompress_function(
                args.target_format,
                args.infile
            )
        except UncompressError as err:
            print("Failed to get decompress function: {}".format(err))
            sys.exit(1)
        additional_args['start_chunk'] = read_chunk

    try:
        method(args.infile, args.outfile, **additional_args)
    except UncompressError as err:
        print("%s: %s" % (err.__class__.__name__, err))
        sys.exit(1)
    except Exception as err:
        print("%s: %s" % (err.__class__.__name__, err))
        sys.exit(2)


if __name__ == "__main__":
    main()
