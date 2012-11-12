import argparse


class ParseArgs:
    def __init__(self, data):
        #untested
        parser = argparse.ArgumentParser.parse_args(data)
        parser.add_argument('--links', dest='links', required=True)
        args = parser.parse_args()
        print args.links

    def send_downloads(self):
        #TODO emit signal, passing all links
        pass