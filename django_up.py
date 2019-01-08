from argparse import ArgumentParser
from init import init
from setup import setup


def deploy():
    print('deploy')


def main():
    parser = ArgumentParser(description='Django up: Deployment tool for django.')
    parser.add_argument('action', choices=['init', 'setup', 'deploy'])
    args = parser.parse_args()
    globals()[args.action]()


if __name__ == "__main__":
    main()
