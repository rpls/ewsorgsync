import logging

import exchangelib as exlib
import re

from .htmltoorg import strip_tags, urlregex

logger = logging.getLogger('org')


def convert_newlines(body):
    # Convert Windows linefeeds
    body = body.replace('\r\n', '\n')
    # Convert MAC linefeeds
    return body.replace('\r', '\n')


def scan_links(body):
    return urlregex.sub(r'[[\1]]', body)


def ewscal_to_org(items,
                  timezone,
                  outfile,
                  date_fmt,
                  datetime_fmt,
                  ignorepattern=None):
    if ignorepattern is not None:
        ignorepattern = re.compile(ignorepattern, re.IGNORECASE)
    for i in items:
        if ignorepattern is not None and ignorepattern.match(i.subject):
            logging.info(
                f'Ignoring appointment "{i.subject}" on {i.start:{date_fmt}}')
            continue
        logging.info(
            f'Adding appointment "{i.subject}" on {i.start:{date_fmt}}')
        print(f'* {i.subject}', file=outfile)
        if i.is_all_day:
            print(f'<{i.start:{date_fmt}}>', file=outfile)
        else:
            start = i.start.astimezone(timezone)
            end = i.end.astimezone(timezone)
            print(f'<{start:{datetime_fmt}}>--<{end:{datetime_fmt}}>',
                  file=outfile)
        if i.body is not None:
            body = convert_newlines(i.body)
            if type(i.body) == exlib.HTMLBody:
                body = strip_tags(body)
            elif type(i.body) == exlib.Body:
                body = scan_links(body)
            else:
                body = ''
                logging.warning('Unknown body type')
            print(body.strip(), file=outfile)
