import pygtk
import gtk
import gobject

#constants
WIDGET, TITLE, CALLBACK, PARAMS = range(4)


class Menu(gtk.Menu):
    """
    Drop down menu, pop-up/context menu.
    """
    def __init__(self, menu_list):
        """
        menu_list = [(gtk.widget, 'title', callback_method, (args, )), ]
        """
        gtk.Menu.__init__(self)
        for menu_item in menu_list:
            if menu_item is None:
                item = gtk.SeparatorMenuItem()
            else:
                item = menu_item[WIDGET]
                item.set_label(menu_item[TITLE])
                try:
                    args = menu_item[PARAMS]
                    item.connect("activate", menu_item[CALLBACK], *args)
                except IndexError:
                    item.connect("activate", menu_item[CALLBACK])
            item.show()
            self.append(item)
