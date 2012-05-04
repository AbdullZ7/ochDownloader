import pygtk
import gtk
import gobject

import os
import sys
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import core.cons as cons


#constants
EXT = ".png"

#sizes
SMALL = "16"
MEDIUM = "24"
LARGE = "48"
SCALABLE = "scalable"

#icons
ARROW_DOWN = "arrow_down_black"
PREFERENCES = "preferences"
START = "start"
STOP = "stop"
ACCOUNTS = "accounts"
ABOUT = "about"
ADD = "add"
DOWN = "down"
REFRESH = "view-refresh"
QUEUE = "queue"
CHECK = "check"
X_MARK = "x-mark"


def get_image(img, size):
    img = img+EXT
    try:
        return gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file(os.path.join(cons.MEDIA_PATH, size, img).decode(sys.getfilesystemencoding())))
    except Exception as err:
        logger.warning(err)
        return gtk.image_new_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_BUTTON)

def get_pixbuf(img, size):
    img = img+EXT
    try:
        return gtk.gdk.pixbuf_new_from_file(os.path.join(cons.MEDIA_PATH, size, img).decode(sys.getfilesystemencoding()))
    except Exception as err:
        logger.warning(err)
        return gtk.Image().render_icon(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_BUTTON)

def get_pixbuf_at_size(img, width, height):
    img = img+EXT
    try:
        return gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(cons.MEDIA_PATH, SCALABLE, img).decode(sys.getfilesystemencoding()), width, height)
    except Exception as err:
        logger.warning(err)
        return gtk.Image().render_icon(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_BUTTON)

def get_image_at_size(img, width, height):
    #UNTESTED
    img = img+EXT
    try:
        return gtk.image_new_from_pixbuf(get_pixbuf(img, LARGE).scale_simple(width, height, gtk.gdk.INTERP_BILINEAR))
    except Exception as err:
        logger.warning(err)
        return gtk.image_new_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_BUTTON)


#_img_buffer = {} #global.
