import logging
import re
from html.parser import HTMLParser

logger = logging.getLogger('htmltoorg')

urlregex = re.compile(
    r'(((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#%])*)')


class HTMLToOrg(HTMLParser):

    IGNORED_TAGS = [
        'head', 'html', 'div', 'span', 'style',
        'font', 'meta', 'br', 'img', 'col', 'colgroup']

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.outstack = []
        self.output = ''
        self.link = None

    def push(self):
        self.outstack.append([])

    def pop(self, joint=' ', filt=lambda x: len(x) > 0):
        try:
            output = list(filter(filt, self.outstack.pop()))
            return joint.join(output)
        except IndexError:
            return ''

    def write(self, text):
        try:
            self.outstack[-1].append(text)
        except IndexError:
            pass

    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.push()
        elif tag in ['p', 'o:p']:
            self.push()
        elif tag == 'a':
            self.push()
            attr = dict(attrs)
            if 'href' in attr:
                self.link = attr['href']
        elif tag == 'table':
            self.push()
        elif tag == 'tr':
            self.push()
        elif tag in ['td', 'th']:
            self.push()
        elif tag == 'u':
            self.push()
        elif tag == 'b':
            self.push()
        elif tag in self.IGNORED_TAGS:
            pass
        else:
            logger.warning(f'Unsupported tag: {tag}')
        pass

    def handle_endtag(self, tag):
        if tag == 'body':
            self.output = self.pop('\n')
        elif tag == 'u':
            output = self.pop()
            # Swallow the u tag if its just to emphasize the same link
            if output != self.link:
                self.write(f'/{output}/')
        elif tag == 'b':
            self.write(f'*{self.pop()}*')
        elif tag in ['p', 'o:p']:
            output = self.pop().strip()
            if len(output) > 0:
                self.write(f'{output}\n')
        elif tag == 'a':
            if self.link is not None:
                output = self.pop()
                if len(output) > 0:
                    self.write(f'[[{self.link}][{output}]]')
                else:
                    self.write(f'[[{self.link}]]')
            else:
                self.write(self.pop())
            self.link = None
        elif tag == 'table':
            self.write(self.pop('\n'))
        elif tag == 'tr':
            self.write(f'| {self.pop("| ")} |')
        elif tag == 'th':
            self.write(f'*{self.pop()}*')
        elif tag == 'td':
            self.write(self.pop())
        elif tag in self.IGNORED_TAGS:
            pass
        else:
            logger.warning(f'Unsupported tag: {tag}')

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            pass
        else:
            logger.warning(f'Unsupported tag: {tag}')

    def handle_data(self, d):
        self.write(d.replace('\xa0', '').strip())

    def get_data(self):
        return self.output


def strip_tags(html):
    s = HTMLToOrg()
    s.feed(html)
    return s.get_data()
