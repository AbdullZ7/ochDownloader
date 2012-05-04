import gtk

import core.cons as cons

from dialog_base import AboutDialog


class AboutGui(AboutDialog): #dialog.
    def __init__(self, parent=None):
        """"""
        AboutDialog.__init__(self)
        self.set_transient_for(parent)
        self.set_program_name(cons.APP_NAME)
        self.set_version(cons.APP_VER)
        self.set_copyright("(c) ochDownloader.com")
        self.set_comments(_("ochDownloader is a simple tool for One Click Hoster automated download"))
        self.set_website("http://www.ochdownloader.com")
        self.run()
        self.destroy()
