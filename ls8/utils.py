def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys
        import termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
