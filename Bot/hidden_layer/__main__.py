import sys


if __name__ == '__main__':
    from hidden_layer import botinitializer

    if '--version' in sys.argv:
        print(botinitializer.__version__)