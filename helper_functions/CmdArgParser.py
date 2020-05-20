# include standard modules
import argparse


def argument_parser():
    # define the program description
    text = 'This is a test program. It demonstrates how to use the argparse module with a program description.'

    # initiate the parser with a description
    parser = argparse.ArgumentParser(description=text)
    parser.add_argument("-a", "-account", dest='account', help="selected account name to run script", nargs="*")
    parser.add_argument("-m", dest='multithreaded', help="# of thread for multithreaded operation", type=int)

    args = parser.parse_args()

    print("\n===================================================================")
    print("COMMAND LINE ARGUMENTS ")
    print("===================================================================")

    if args.account:
        print(f"LOG INFO: ACCOUNT FLAG SET: {args.account}")

    if args.multithreaded:
        if args.multithreaded > 1:
            print(f"LOG INFO: MULTITHREAD FLAG: {args.multithreaded}")
        else:
            print("LOG INFO: SINGLE THREADED OPERATION")

    return args


if __name__ == '__main__':
    argument_parser()
