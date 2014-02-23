#! /usr/bin/python3

from . import utils


if __name__ == "__main__":
    #path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "")
    path = "C:\\Users\\Admin\\PycharmProjects\\ochd_2\\ochDownloader"
    modules = utils.extract_imports([path, ])
    print(modules)