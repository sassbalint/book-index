"""
Detokenize emtsv output.
Create a lemmatized version of the original file.
"""

import argparse
import sys


def main():
    """Do the thing."""
    args = get_args()

    for line in sys.stdin:
        line = line.strip()
        if len(line) > 0:
            fields = line.split('\t')

            wordform = fields[0]
            wsafter = fields[1].strip('"')
            ana = fields[2].lstrip('[').rstrip(']')
            # XXX vhogy előfordul, hogy nincs lemma?
            lemma = fields[3] if len(fields) >= 4 else ""

            # important trick:
            # we need all the weird wordforms
            # -> we turn off / ignore the guesser
            # that means: if there is no analysis
            # take the wordform as lemma
            if len(ana) == 0: # empty string
                lemma = wordform

            wsafter = wsafter.replace('\\n', '\n')
            wsafter = wsafter.replace('\\t', '\t')
            wsafter = wsafter.replace('\\f', '\f')

            print(f'{lemma}{wsafter}', end='')


def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    return parser.parse_args()


if __name__ == '__main__':
    main()
