from plugins.uploaded.link_checker import LinkChecker as link_checker


class LinkChecker:
    def check(self, link):
        return link_checker().check(link)