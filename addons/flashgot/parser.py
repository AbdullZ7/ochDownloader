import argparse


class ParseArgs:
    def __init__(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('-l', '--links', dest='links', required=True)
        p = parser.parse_args(args=args)
        print p.links

    def send_downloads(self):
        #TODO emit signal, passing all links
        pass