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
        args = self.re_parse(args)
        try:
            p = self.parse_args(args=args)
        except Exception as err:
            logger.warning(err)
        else:
            print p.links
            cj = self.load_cookie(p.cookie)

    def re_parse(self, args):
        # fixes links list
        new_args = []
        links = []
        for arg in args:
            if arg.startswith("http"):
                links.append(arg)
            elif arg != "--links":
                new_args.append(arg)
        new_args.append("--links")
        links_ = " ".join(links)
        new_args.append(links_)
        return new_args

    def load_cookie(self, path):
        cj = cookielib.MozillaCookieJar()
        cj.magic_re = '' # fixes LoadError, netscape header comment checking.
        try:
            cj.load(path)
        except Exception as err:
            logger.warning(err)
            return None
        else:
            return cj