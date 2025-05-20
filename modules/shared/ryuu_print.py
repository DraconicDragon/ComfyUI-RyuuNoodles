def ryuu_print(*args, sep=" ", end="\n", file=None, flush=False):
    """Custom print function that prefixes prints with [RyuuNoodles]."""
    prefix = "\033[38;5;81m[\033[38;5;213mRyuu\033[38;5;213mNoodles\033[38;5;81m]\033[0m"
    print(prefix, *args, sep=sep, end=end, file=file, flush=flush)
