from argparse import ArgumentParser
from dockdj.init import init
from dockdj.setup import setup
from dockdj.deploy import deploy, one_off, stop, restart, logs


def main():
    parser = ArgumentParser(description='Django up: Deployment tool for django.')
    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        help='Show all output from server')
    action_parser = parser.add_subparsers(
        title='action',
        description='Specify action to be performed by django_up',
        dest='action',
        required=True)
    action_parser.add_parser('init', help='Create settings files which will be used to deploy')
    action_parser.add_parser('setup', help='Installs docker in the server')
    action_parser.add_parser('deploy', help='Deploys the django app to server')
    action_parser.add_parser('stop', help='Stop the django app to server')
    action_parser.add_parser('restart', help='Restart the django app to server')

    logs_parser = action_parser.add_parser('logs', help='Show logs of all docker containers')
    logs_parser.add_argument('-f', action='store_true')

    one_off_parser = action_parser.add_parser(
        'one-off',
        help='Runs the django manage command on first configured container.')
    one_off_parser.add_argument('action_args', nargs='*')

    args = parser.parse_args()
    if args.action == 'one-off':
        one_off(args=args.action_args, verbose=args.verbose)
    elif args.action == 'logs':
        logs(follow=args.f, verbose=args.verbose)
    else:
        globals()[args.action](verbose=args.verbose)


if __name__ == "__main__":
    main()
