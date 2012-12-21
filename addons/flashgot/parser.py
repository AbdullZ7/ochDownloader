import cookielib
import logging
logger = logging.getLogger(__name__)

from argparse import ArgumentParser


class ParseArgs(ArgumentParser):
    def __init__(self, args):
        ArgumentParser.__init__(self)
        self.add_argument('-l', '--links', dest='links', required=True)
        self.add_argument('-c', '--cookie', dest='cookie')
        self.add_argument('-p', '--path', dest='path')
        self.send_downloads(args)

    def error(self, message):
        #overriden
        raise Exception(message)

    def send_downloads(self, args):
        #TODO emit signal, passing all links
        #join http: links
        print args
        try:
            p = self.parse_args(args=args)
        except Exception as err:
            logger.warning(err)
        else:
            print p.links
            cj = cookielib.MozillaCookieJar()
            cj.magic_re = '' # fixes LoadError, netscape header comment checking.
            cj.load(p.cookie)