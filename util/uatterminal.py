#!/usr/bin/python

from websockets.__main__ import main
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.argv.append("ws://localhost:65399")
    elif sys.argv[1][0:5] != "ws://" and sys.argv[1][0:6] != "wss://":
        if ":" not in sys.argv[1]:
            sys.argv[1] = "ws://" + sys.argv[1] + ":65399"
        else:
            sys.argv[1] = "ws://" + sys.argv[1]
    main()
