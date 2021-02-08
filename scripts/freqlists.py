"""
Freqlist utils.
Main point: compare two freqlists.
Plan is to do this in several more or less principled ways. :)
"""

import argparse
import sys
from collections import defaultdict
from math import log10


class FreqList:

    def __init__(self, dic, sumcnt):
        """'dic' contains the freqlist as {item: cnt}.
           'sumcnt' is the sum of cnt."""
        self.sumcnt = sumcnt
        self.dic = defaultdict(lambda: defaultdict(int),
            {word: {'cnt': cnt, 'freq': cnt/sumcnt}
                for word, cnt in dic.items()})

    def __getitem__(self, key):
        return self.dic[key]

    def __str__(self):
        return f'{self.dic}'


# XXX vhogy értelmesen betenni az alábbiakat a FreqList -be!
# XXX mert az a tippem, hogy odavalók!
def read(filename):
    """Read a 'freq TAB word' freqlist from file."""
    with open(filename, encoding='utf-8') as freqlistfile:
        dic = defaultdict(int)
        cnt = 0
        for line in freqlistfile:
            fields = line.strip().split('\t')
            if len(fields) == 2: # this should not be 1...
                freq, word = fields
                freq = int(freq) # how to be more pythonic?
                dic[word] = freq
                cnt += freq
    return FreqList(dic, cnt)


def compare(fl1, fl2, head=10, verbose=False):
    """Compare two freqlists.
       Return 'head' pieces of most extreme words on both sides."""

    def smooth(x):
        """Some smooting will maybe needed. How to do it?"""
        #return sys.float_info.epsilon if x == 0 else x # XXX bad!
        return x

    merged = defaultdict(float)
    for word in set(fl1.dic) | set(fl2.dic):

        f1, f2 = fl1[word], fl2[word]
        f1f, f2f = f1['freq'], f2['freq']

        if f2f == 0: f2f = smooth(f2f) # smoothing f2f

        if f1f > 0 and f2f > 0:
            merged[word] = {
                'logratio': log10(f1f / f2f), # log-ratio
                'cnt': [f1['cnt'], f2['cnt']],
            }

    # sort by -x[1]['logratio'] = log-ratio
    # ... and then by x[0] = word
    sorted_merged = sorted(merged.items(),
        key=lambda x: (-x[1]['logratio'], x[0]))

    beg, end = sorted_merged[:head], sorted_merged[-head:]
    if verbose == False:
        beg, end = [x[0] for x in beg], [x[0] for x in end]

    return beg, end


def main():
    """Testing."""
    args = get_args()

    fl1 = read(args.freqlist_one)
    fl2 = read(args.freqlist_two)

    wl1, wl2 = compare(fl1, fl2, head=args.head, verbose=args.verbose)

    for w in wl1 + ['.', '.', '.'] + wl2:
        print(w)


def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-1', '--freqlist-one',
        help='first freqlist to compare',
        type=str,
        default=argparse.SUPPRESS,
        required=True
    )
    parser.add_argument(
        '-2', '--freqlist-two',
        help='second freqlist to compare',
        type=str,
        default=argparse.SUPPRESS,
        required=True
    )
    parser.add_argument(
        '-H', '--head',
        help='display this many items at both sides',
        type=int,
        default=100
    )
    parser.add_argument(
        '-v', '--verbose',
        help='verbose output',
        action='store_true'
    )
    
    return parser.parse_args()


if __name__ == '__main__':
    main()
