import argparse
import configparser
import datetime
import logging
import os.path
import sys

import exchangelib as exlib
import keyring

from ewsorgsync.ewstoorg import ewscal_to_org


def connect_ews(config):
    domain = config.get('domain', None)
    username = config['username']
    if domain is not None:
        username = f'{domain}\\{username}'
    password = config.get('password', None)
    if password is None:
        password = keyring.get_password('ewsorgsync', username)
    if password is None:
        logging.error(
            'Can\'t find password (neither in config nor in keychain)')
        sys.exit(-1)
    cred = exlib.Credentials(username, password)
    ewsconf = exlib.Configuration(credentials=cred,
                                  service_endpoint=config['endpoint'])
    logging.debug('Connecting to endpoint')
    acc = exlib.Account(primary_smtp_address=config['email'], config=ewsconf,
                        default_timezone=exlib.EWSTimeZone.localzone(),
                        access_type=exlib.DELEGATE
                        )
    logging.debug('Refreshing folders')
    acc.root.refresh()
    return acc


def fetch_items(acc, timeframe):
    start = acc.default_timezone.localize(exlib.EWSDateTime.now())
    end = start + datetime.timedelta(days=timeframe)
    start -= datetime.timedelta(days=1)
    logging.info(
        f'Fetching calender items from {start:%Y-%m-%d} to {end:%Y-%m-%d}')
    return acc.calendar.view(start=start, end=end)


def parse_arguments():
    parser = argparse.ArgumentParser(description='EWS to org-mode sync')
    parser.add_argument('-c', '--config', default=None,
                        type=argparse.FileType('r'),
                        help='Config file'
                        )
    parser.add_argument('-v', '--verbose', default=False,
                        action='store_true',
                        help='Verbose logging'
                        )

    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    configfile = args.config
    if configfile is None:
        configfile = os.path.expanduser('~/.ewsorgsyncrc')
    if not os.path.exists(configfile):
        logging.error(f'Can\'t find config file "{configfile}"!')
    config = configparser.ConfigParser()
    config.read(configfile)
    for service in config.sections():
        cfg = config[service]
        acc = connect_ews(cfg)
        outfile = os.path.expanduser(cfg['output'])
        if outfile is None:
            logging.error(f'Config option "{outfile}" unset!')
            sys.exit(-1)
        logging.info(f'Syncing account {service} to file "{outfile}"')
        items = fetch_items(acc, cfg.getint('timeframe', 14))
        with open(outfile, 'w') as outfile:
            ewscal_to_org(items, acc.default_timezone, outfile)


if __name__ == '__main__':
    main()
