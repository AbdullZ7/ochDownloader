import logging
logger = logging.getLogger(__name__)

from argparse import ArgumentParser


class ParseArgs(ArgumentParser):
    def __init__(self, args):
        ArgumentParser.__init__(self)
        self.add_argument('-l', '--links', dest='links', required=True)
        self.send_downloads(args)

    def send_downloads(self, args):
        #TODO emit signal, passing all links
        print args
        try:
            p = self.parse_args(args=args)
        except Exception as err:
            logger.exception(err)
        else:
            print p.links