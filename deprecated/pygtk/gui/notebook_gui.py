import gtk
import pygtk


class Notebook(gtk.Notebook):
    """"""
    def __init__(self):
        """"""
        gtk.Notebook.__init__(self)
    
    def insert_closable_page(self, widget, label, index_page=-1):
        #hbox will be used to store a label and button, as notebook tab title
        hbox = gtk.HBox(False, 0)
        #label = gtk.Label(title)
        hbox.pack_start(label, False, False)

        #get a stock close button image
        close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        image_w, image_h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
        
        #make the close button
        btn = gtk.Button()
        btn.set_relief(gtk.RELIEF_NONE)
        btn.set_focus_on_click(False)
        btn.add(close_image)
        hbox.pack_start(btn, False, False)
        btn.set_size_request(image_w + 4, image_h)

        #this reduces the size of the button
        style = gtk.RcStyle()
        style.xthickness = 0
        style.ythickness = 0
        btn.modify_style(style)

        hbox.show_all()

        #the tab will have a single widget: a label
        #widget = gtk.Label(title) #remove
        
        #add the tab
        self.insert_page(widget, hbox, index_page) #hbox = label+close_button

        btn.connect('clicked', self.on_closetab_button_clicked, widget)

    def on_closetab_button_clicked(self, sender, widget):
        #get the page number of the tab we wanted to close
        pagenum = self.page_num(widget)
        #and close it
        widget.on_close() #every widget added need to have this method.
        self.remove_page(pagenum)


if __name__ == "__main__":
        w = gtk.Window()
        w.connect("destroy", lambda wid: gtk.main_quit())
        w.connect("delete_event", lambda a1,a2:gtk.main_quit())
        w.set_size_request(600, 400)
        
        #Create a notebook
        #self.notebook = gtk.Notebook()
        notebook = Notebook()
        for x in xrange(1, 10):
            title="Tab" + str(x)
            widget = gtk.Label(title)
            notebook.insert_closable_page(widget, gtk.Label(title))
        notebook.append_page(gtk.Label(title), gtk.Label(title))
            
        w.add(notebook)
        w.show_all()
        gtk.main()
