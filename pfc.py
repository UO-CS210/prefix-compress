"""Prefix compression and decompression of a world list file."""

import sys
import argparse
import codec

def cli() -> argparse.Namespace:
    """Command line interface.
    Usage is
        python3 pfc compress <infile> <outfile>
        python3 pfc expand <infile> <outfile>
    """
    parser = argparse.ArgumentParser("Prefix encoding compressor/decompressor for sorted word lists")
    parser.add_argument("operation", choices=["compress", "expand"])
    parser.add_argument("infile", type=argparse.FileType("r"),
                        nargs="?", default=sys.stdin)
    parser.add_argument("outfile", type=argparse.FileType("w"),
                        nargs="?", default=sys.stdout)
    return parser.parse_args()

def main():
    args = cli()
    prior = ""

    for line in args.infile:
        word = line.strip()
        if args.operation == "compress":
            converted = codec.encode(word, prior)
            prior = word
        else:
            converted = codec.decode(word, prior)
            prior = converted
        print(converted, file=args.outfile)

    args.infile.close()
    args.outfile.close()

if __name__ == "__main__":
    main()




