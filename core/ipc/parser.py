import cookielib
import logging
logger = logging.getLogger(__name__)

from argparse import ArgumentParser


class ArgumentError(Exception): pass


class ParseArgs(ArgumentParser):
    def __init__(self, args):
        ArgumentParser.__init__(self)
        self.add_argument('-i', '--ipc', dest='ipc', default=False)
        self.add_argument('-l', '--links', dest='links', required=True)
        self.add_argument('-c', '--cookie', dest='cookie')
        self.add_argument('-p', '--path', dest='path')
        self.arguments = self.parse_args(args=args)

    def error(self, message):
        #overriden
        raise ArgumentError(message)

    def parse_args(self, *args, **kwargs):
        args = kwargs.get("args", None)
        if args is not None and "--links" in args:
            new_args = self.format_links(args)
            kwargs["args"] = new_args
        return ArgumentParser.parse_args(self, *args, **kwargs)

    def send_downloads(self, args):
        #TODO emit signal, passing all links
        # add an option so if there is no --path, we can set a default path or add to checking otherwise
        if self.arguments.cookie is not None:
            cj = self.load_cookie(self.arguments.cookie)

    def format_links(self, args):
        """
        converts:
            ["--links", "http:...", "http:...", "http:...", ...]
        to:
            ["--links", "http:... http:... http:...", ...]
        """
        new_args = []
        links = []
        for arg in args:
            if arg.startswith("http", "och:"):
                arg = arg.replace("och://", "http://")
                links.append(arg)
            elif arg != "--links":
                new_args.append(arg)
        if links:
            new_args.append("--links")
            nice_links = " ".join(links)
            new_args.append(nice_links)
            return new_args
        else:
            return args

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