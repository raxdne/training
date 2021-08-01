#!/usr/bin/python3

"""
 (setq python-shell-interpreter "/usr/bin/python3")
 (local-set-key [f3] (lambda () "" (interactive)(save-buffer)(python-shell-send-buffer)))
"""

import argparse
import glob
import datetime

from training import training


def parse_args(args=None):

    # https://docs.python.org/3/howto/argparse.html
    parser = argparse.ArgumentParser(
        description='Dump .CSV training files to various formats',
        epilog='python-fitparse version ',
    )
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument(
        '-o', '--output', type=argparse.FileType(mode='w'), default="-",
        help='File to output data into (defaults to stdout)',
    )
    parser.add_argument(
        '-t', '--type', choices=('readable', 'json', 'mm', 'csv', 'xml', 'ics', 'svg', 'sqlite'), default='readable',
        help='File type to output. (DEFAULT: %(default)s)',
    )
    parser.add_argument(
        'infile', nargs="+", type=str,
        help='Input .CSV file (Use - for stdin)',
    )

    options = parser.parse_args(args)
    options.verbose = options.verbose >= 1
    options.with_defs = (options.type == "readable" and options.verbose)
    options.as_dict = (options.type != "readable" and options.verbose)

    return options


def main(args=None):

    options = parse_args(args)

    s = training.period('Report ' + datetime.date.today().isoformat())
    s.parseFile(options.infile)
    training.max_length_type = 1
    #training.unit_distance = 'mi'
    
    try:
        if options.type == "xml":
            # TODO: generic XML output
            pass
        elif options.type == "sqlite":
            # TODO: sqlite output
            pass
        elif options.type == "json":
            # TODO: JSON output
            pass
        elif options.type == "csv":
            print(s.toCSV(), file=options.output)
        elif options.type == "ics":
            print(s.toVCalendar(), file=options.output)
        elif options.type == "svg":
            print(s.toSVGDiagram(), file=options.output)
        elif options.type == "mm":
            print(s.toFreeMind(), file=options.output)
        else:
            print(s.stat(), file=options.output)
            
    finally:
        try:
            options.output.close()
        except IOError:
            pass


if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError:
        pass
        
