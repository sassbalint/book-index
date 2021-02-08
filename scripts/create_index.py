"""
Create an index for a book.
Collect index-words comparing the freqlist of the book
to a freqlist of general text.
"""

import argparse
from collections import defaultdict
from functools import cmp_to_key
import locale

import freqlists as fl

locale.setlocale(locale.LC_ALL, 'hu_HU.UTF-8')


def merge_adjacent(intlist):
    """Param: list of integers (!) sorted (!)
       Merge adjacent integers in thgelist.
       Return a list of strings.
       [1, 4, 5, 6, 8, 9, 12] -> ['1', '4-6', '8-9', '12']"""

    def format_item(beg, end):
        return f'{beg}-{end}' if beg < end else f'{beg}'

    if len(intlist) == 0:
        return []

    strlist = []
    beg = end = intlist.pop(0)
    for i in intlist:
        if i == end + 1: # this means: adjacent
            end += 1
        else:
            strlist.append(format_item(beg, end))
            beg = end = i
    strlist.append(format_item(beg, end))
    return strlist


def next_alphabet_letter(initial, word):
    """Determine whether word compared to initial
       is "in a new letter" when creating a dictionary.
       'b' compared to 'a' is a new letter indeed.
       'á' compared to 'a' is not new
       according to Hungarian rules!"""

    # the trick is: 'az' > 'áa' (while 'a' < 'á')

    word_first1 = word[0:1]  # a, á, b, c ...
    word_first2 = word[0:2]  # cs, dz ...
    word_first3 = word[0:3]  # dzs

    digraph = {'cs', 'dz', 'gy', 'ly', 'ny', 'sz', 'ty', 'zs'}
    trigraph = {'dzs'}

    if locale.strcoll(initial + 'z', word_first1 + 'a') < 0:
        return word_first1
    if (word_first2 in digraph and
        locale.strcoll(initial + 'z', word_first2 + 'a') < 0):
        return word_first2
    if (word_first3 in trigraph and
        locale.strcoll(initial + 'z', word_first3 + 'a') < 0):
        return word_first3
    else:
        return initial
    # hogy csináltam meg vajon az iszgysz szótárnál? :)
    # sztem hardkódolt listával... :)


def dict_initial(letter):
    """Create header from Hungarian letters
       taking equivalent letters into account."""
    double_letters = ['aá', 'eé', 'ií', 'oó', 'öő', 'uú', 'üű']
    for dl in double_letters:
        if letter in dl:
            return f'{dl[0]}, {dl[1]}'
            break
    else:
        return letter


def main():
    """Do the thing."""
    args = get_args()

    book = defaultdict(set)
    # folytonos oldalszámonként van, így "logikusabb" lenne a lista...
    with open(args.book, encoding='utf-8') as bookfile:
        for line in bookfile:
            pagenum, _, text = line.strip().partition('\t')
            book[int(pagenum)].update(text.split(' '))

    exclude = set()
    if args.exclude_list is not None:
        with open(args.exclude_list, encoding='utf-8') as excludefile:
            exclude.update(line.strip() for line in excludefile)

    include = set()
    if args.include_list is not None:
        with open(args.include_list, encoding='utf-8') as includefile:
            include.update(line.strip() for line in includefile)

    fl1 = fl.read(args.book_freqlist)
    fl2 = fl.read(args.general_freqlist)

    index_words, _ = fl.compare(fl1, fl2, head=args.number_of_words)

    index_words = set(index_words) - exclude | include

    # magyar sorrend!
    # https://medium.com/the-programming-hub/how-to-sort-a-list-of-strings-in-python-345e43b4c2b8
    sorted_index_words = sorted(index_words,
        key=cmp_to_key(locale.strcoll))

    initial_letter = '0' # minimal extremal element needed...
    for word in sorted_index_words:
        pagenums = []

        for pagenum in book:
            if word in book[pagenum]:
                pagenums.append(pagenum)

        if len(pagenums) > 0:
            new_initial_letter = next_alphabet_letter(initial_letter, word)
            if new_initial_letter != initial_letter:
                initial_letter = new_initial_letter
                print(f'## {dict_initial(initial_letter)}')
            merged_pagenums = ", ".join(merge_adjacent(pagenums))
            print(f'__{word}__ {merged_pagenums}  ')


def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-b', '--book',
        help='a text for which we create an index, prepended with page numbers line by line',
        type=str,
        default=argparse.SUPPRESS,
        required=True
    )
    parser.add_argument(
        '-f', '--book-freqlist',
        help='freqlist of BOOK',
        type=str,
        default=argparse.SUPPRESS,
        required=True
    )
    parser.add_argument(
        '-g', '--general-freqlist',
        help='a general freqlist for comparison',
        type=str,
        default=argparse.SUPPRESS,
        required=True
    )
    parser.add_argument(
        '-n', '--number-of-words',
        help='size of the index',
        type=int,
        default=100,
        required=False
    )
    parser.add_argument(
        '--exclude-list',
        help='file containing words which should not appear in index',
        type=str,
        required=False
    )
    parser.add_argument(
        '--include-list',
        help='file containing words which must appear in index',
        type=str,
        required=False
    )
    
    return parser.parse_args()


if __name__ == '__main__':
    main()
