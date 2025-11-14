#!/usr/bin/env python3
from engine import run
from utils import load_metadata, save_metadata
from core import create_table


def main():
    print('DB project is running!')
    run()

if __name__ == '__main__':
    main()