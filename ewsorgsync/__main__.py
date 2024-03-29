import argparse
import configparser
import datetime
import logging
import os.path
import sys

import exchangelib as exlib
import exchangelib.items as exlibit
import keyring

from ewsorgsync.ewstoorg import ewscal_to_org


def connect_ews(config):
    domain = config.get('domain', None)
    username = config.get('username', None)
    email = config.get('email', None)
    if username is not None and domain is not None:
        username = f'{domain}\\{username}'
    else:
        username = f'{email}'
    password = config.get('password', None)
    if password is None:
        password = keyring.get_password('ewsorgsync', username)
    if password is None:
        logging.error(
            'Can\'t find password (neither in config nor in keychain)')
        sys.exit(-1)
    if domain is not None:
        username = f'{domain}\\{username}'
    else:
        username = f'{email}'
    cred = exlib.Credentials(username, password)
    endpoint = config.get('endpoint', None)
    server = config.get('server', None)
    if endpoint is not None and server is not None:
        logging.error(
            'The server and endpoint options are mutually exclusive!')
        sys.exit(-1)
    elif endpoint is None and server is None:
        logging.error(
            'You must give either the server or endpoint option!')
        sys.exit(-1)
    conf = {
        'server': server,
        'service_endpoint': endpoint
    }
    ewsconf = exlib.Configuration(credentials=cred,
                                  **conf)
    logging.debug('Connecting to endpoint')
    acc = exlib.Account(primary_smtp_address=config['email'],
                        config=ewsconf,
                        default_timezone=exlib.EWSTimeZone.localzone(),
                        access_type=exlib.DELEGATE)
    logging.debug('Refreshing folders')
    acc.root.refresh()
    return acc


def fetch_items(acc, timeframe):
    start = exlib.EWSDateTime.now().replace(tzinfo=acc.default_timezone)
    end = start + datetime.timedelta(days=timeframe)
    start -= datetime.timedelta(days=1)
    logging.info(
        f'Fetching calender items from {start:%Y-%m-%d} to {end:%Y-%m-%d}')
    return acc.calendar.view(start=start, end=end)


def fetch_requests(acc):
    # IPython.embed()
    for req in acc.inbox.filter(item_class__contains='Meeting').order_by('-datetime_received'):
        if isinstance(req, exlibit.MeetingRequest):
            print(f'Meeting Request: {req.subject}')
            IPython.embed()
        elif isinstance(req, exlibit.MeetingCancellation):
            print(f'Meeting Cancellation: {req.subject}')
            IPython.embed()


def parse_arguments():
    parser = argparse.ArgumentParser(description='EWS to org-mode sync')
    parser.add_argument('-c',
                        '--config',
                        default=None,
                        type=argparse.FileType('r'),
                        help='Config file')
    parser.add_argument('-v',
                        '--verbose',
                        default=False,
                        action='store_true',
                        help='Verbose logging')
    parser.add_argument('-i', '--interactive', default=False,
                        action='store_true',
                        help='Interactively go through meeting requests')
    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    configfile = args.config
    config = configparser.ConfigParser()
    if configfile is None:
        configfile = os.path.expanduser('~/.ewsorgsyncrc')
        config.read(configfile)
    else:
        config.read_file(configfile)
    for service in config.sections():
        cfg = config[service]
        acc = connect_ews(cfg)
        outfile = os.path.expanduser(cfg['output'])
        if outfile is None:
            logging.error(f'Config option "{outfile}" unset!')
            sys.exit(-1)
        if args.interactive:
            # calitems = fetch_items(acc, cfg.getint('timeframe', 14))
            logging.info(f'Fetching requests from account {service}')
            reqitem = fetch_requests(acc)
            # for item in reqitem:
            #     print(f'Meeting Request: {item.subject}')
            pass
        else:
            logging.info(f'Syncing account {service} to file "{outfile}"')
            items = fetch_items(acc, cfg.getint('timeframe', 14))
            with open(outfile, 'w') as outfile:
                ewscal_to_org(items, acc.default_timezone, outfile,
                              cfg.get('date_fmt', '%Y-%m-%d', raw=True),
                              cfg.get('datetime_fmt', '%Y-%m-%d %H:%M', raw=True),
                              cfg.get('ignorepattern', fallback=None, raw=True))


if __name__ == '__main__':
    main()
