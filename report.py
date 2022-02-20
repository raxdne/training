#!/usr/bin/python3

"""
"""

import argparse
import glob
import datetime

import training as config

from unit import Unit

from cycle import Cycle

from period import Period


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
        '-t', '--type', choices=('readable', 'json', 'mm', 'csv', 'html', 'xml', 'ics', 'svg', 'sqlite'), default='readable',
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

    s = Period('Report ' + datetime.date.today().isoformat())
    s.parseFile(options.infile)
    config.max_length_type = 1
    #config.unit_distance = 'mi'
    
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
        elif options.type == "html":
            print(s.toHtmlFile(), file=options.output)
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
        
