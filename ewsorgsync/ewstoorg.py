import logging

import exchangelib as exlib

from .htmltoorg import strip_tags, urlregex

logger = logging.getLogger('org')


def convert_newlines(body):
    # Convert Windows linefeeds
    body = body.replace('\n\r', '\n')
    # Convert MAC linefeeds
    return body.replace('\r', '\n')


def scan_links(body):
    return urlregex.sub(r'[[\1]]', body)


def ewscal_to_org(items, timezone, outfile):
    for i in items:
        logging.info(f'Adding appointment "{i.subject}" on {i.start:%Y-%m-%d}')
        print(f'* {i.subject}', file=outfile)
        if i.is_all_day:
            print(f'<{i.start:%Y-%m-%d}>', file=outfile)
        else:
            start = i.start.astimezone(timezone)
            end = i.end.astimezone(timezone)
            print(f'<{start:%Y-%m-%d %H:%M}>--<{end:%Y-%m-%d %H:%M}>',
                  file=outfile)
        if i.body is not None:
            if type(i.body) == exlib.HTMLBody:
                body = strip_tags(i.body)
            elif type(i.body) == exlib.Body:
                body = scan_links(i.body)
            else:
                body = ''
                logging.warning('Unknown body type')
            print(body.strip(), file=outfile)
