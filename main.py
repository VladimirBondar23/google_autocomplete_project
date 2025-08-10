import sys

import database as db
import algo as al

def main():
    dir_name = sys.argv[1]
    db.store_lines(dir_name)
    while (True):
        word = input()
        al.search(word)


if __name__ == '__main__':
    main()

