from argparse import ArgumentParser
from dockdj.init import init
from dockdj.setup import setup
from dockdj.deploy import deploy
from dockdj.logs import logs


def main():
    parser = ArgumentParser(description='Django up: Deployment tool for django.')
    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        help='Show all output from server'
    )
    action_parser = parser.add_subparsers(
        title='action',
        description='Specify action to be performed by django_up',
        dest='action',
        required=True
    )
    action_parser.add_parser('init', help='Create settings files which will be used to deploy')
    action_parser.add_parser('setup', help='Installs docker in the servers')
    action_parser.add_parser('deploy', help='Deploys the django app to servers')
    action_parser.add_parser('logs', help='Show logs of all docker containers')

    args = parser.parse_args()
    globals()[args.action](verbose=args.verbose)


if __name__ == "__main__":
    main()
