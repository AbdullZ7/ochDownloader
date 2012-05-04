#!/usr/bin/env python

# This file is based on http://git.gnome.org/browse/pygtk/tree/examples/gtk/treeview_dnd.py
# wich is based on http://code.google.com/p/quodlibet/source/browse/junk/dndtest.py
# more examples: http://git.gnome.org/browse/pygtk/tree/examples/gtk
# windows bug: https://bugzilla.gnome.org/show_bug.cgi?id=641924
# tutorial: http://www.pygtk.org/pygtk2tutorial/sec-TreeViewDragAndDrop.html

import pygtk
import gobject
import gtk

import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#import core.cons as cons
from core.api import api


class DnDTreeView(gtk.TreeView):
    """
    Fully independent class :)
    """
    def __init__(self, model): #store_model or tree_model
        gtk.TreeView.__init__(self)
        
        self.item_list = []
        self.__iters = []
        self.rows_buffer = {} #{id_item: row_obj, }
        
        self.set_model(model)
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        #drag n drop tree items only.
        targets = [
                        ('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
                        #('text/uri-list', 0, 1)
                        #('text/plain', 0, 2),
                        #('TEXT', 0, 3),
                        #('STRING', 0, 4),
                        ]
        #enable_model_drag_source and enable_model_drag_dest wont work on Windows.
        #http://www.pygtk.org/pygtk2reference/gdk-constants.html#gdk-modifier-constants
        #gtk.gdk.BUTTON1_MASK = first mouse button. gtk.gdk.CONTROL_MASK = Control key.
        #self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK | gtk.gdk.CONTROL_MASK,
                                                #targets,
                                                #gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        #gtk.gdk.ACTION_COPY = Copy the data. gtk.gdk.ACTION_MOVE = Move the data, i.e. first copy it, then delete it.
        #self.enable_model_drag_dest(targets,
                                            #gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_DEFAULT)
        self.drag_source_set(gtk.gdk.BUTTON1_MASK | gtk.gdk.CONTROL_MASK,
                             targets,
                             gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        self.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                           targets,
                           gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        self.connect('drag-begin', self._drag_begin)
        #self.connect('drag-data-delete', self._drag_data_delete)
        self.connect('drag-motion', self._drag_motion)
        self.connect('drag-data-get', self._drag_data_get)
        self.connect('drag-data-received', self._drag_data_received)
        #self.connect('drag-end', self._drag_end)
    
    def get_id_item_list(self):
        """
        Devolver ids de todos los items.
        """
        model = self.get_model()
        return [row[0] for row in model]
    
    def _drag_end(self, view, ctx):
        print "_drag_end"
        if self.item_list:
            #self.reorder_queue(self.item_list, self.iditem_dest, self.insert_before)
            item_id_list = self.get_id_item_list()
            api.reorder_queue(item_id_list) #iditem_list
        del self.item_list[:]
        
        return True

    def _drag_begin(self, view, ctx):
        print "drag_begin"
        return True

    def _drag_data_delete(self, view, ctx):
        print "drag_data_delete"
        #if ctx.is_source and ctx.action == gtk.gdk.ACTION_MOVE:
            # For some reason this gets called twice.
        model = self.get_model()
        [model.remove(iter) for iter in self.__iters]
        del self.__iters[:]

    def _drag_motion(self, view, ctx, x, y, time):
        model, rows = self.get_selection().get_selected_rows()
        if rows:
            try:
                row, pos = self.get_dest_row_at_pos(x, y)
                self.set_drag_dest_row(row, pos)
            except TypeError:
                self.set_drag_dest_row(len(self.get_model()) - 1, gtk.TREE_VIEW_DROP_AFTER)

            #if ctx.get_source_widget() == self:
            kind = gtk.gdk.ACTION_MOVE
            #else:
                #kind = gtk.gdk.ACTION_COPY

            ctx.drag_status(kind, time)
        return True

    def _drag_data_get(self, view, ctx, selection, target_id, etime): #target_id = id defined on targets.
        print "drag_data_get"
        model, rows = self.get_selection().get_selected_rows()
        
        if rows:
            for row in rows:
                self.__iters.append(model[row].iter)
                #nested lists [item1=[col_1, col2, col_3], item2=[col_1, col_2. col_3], ]
                self.item_list.append([item_col for item_col in model[row]])
            
            #nested lists [item1=[col_1, col2, col_3], item2=[col_1, col_2. col_3], ]
            #self.item_list = [[item_col for item_col in model[row]] for row in rows] #nested list comprehension.
            #if ctx.action == gtk.gdk.ACTION_MOVE:
            #self.__iters = [model[row].iter for row in rows]
            #else:
                #self.__iters = []
            
            #http://www.pygtk.org/docs/pygtk/class-gtkselectiondata.html
            #selection.tree_set_row_drag_data(model, paths)
            #Not needed when using enable_model_drag_source. when that doesnt work on Windows.
            selection.set(selection.target, 8, data="") #just to call drag_data_received.
                
        return True

    def _drag_data_received(self, view, ctx, x, y, selection, info, etime): #widget, drag_context, x, y, selection_data, info, timestamp. info = destination id (int) target_id
        """
        widget is the TreeView, drag_context is a DragContext containing the context of the selection,
        x and y are the position where the drop occurred, selection_data is the SelectionData containing the data,
        info is the ID integer of the type, timestamp is the time when the drop occurred.
        """
        print "drag_data_received"
        model = view.get_model()
        
        if self.item_list:
            #files = selection.data
            item_list_copy = self.item_list[:]

            try:
                path, position = self.get_dest_row_at_pos(x, y)
            except TypeError:
                path, position = len(model) - 1, gtk.TREE_VIEW_DROP_AFTER
            
            iter = model.get_iter(path)
            #try:
            first_item = item_list_copy.pop(0)
            #except IndexError as err:
                #return True
            
            if position in (gtk.TREE_VIEW_DROP_BEFORE, gtk.TREE_VIEW_DROP_INTO_OR_BEFORE): #encima o antes.
                iter = model.insert_before(iter, first_item)
                row = model.get_path(iter)
                self.rows_buffer[model[row][0]] = model[row]
            else: #when drops at the bottom and before first item.
                iter = model.insert_after(iter, first_item)
                row = model.get_path(iter)
                self.rows_buffer[model[row][0]] = model[row]
            for item in item_list_copy: #when dragin more than one element
                iter = model.insert_after(iter, item)
                row = model.get_path(iter)
                self.rows_buffer[model[row][0]] = model[row]
            
            #if ctx.action != gtk.gdk.ACTION_MOVE:
            #ctx.finish(True, etime)
            self._drag_data_delete(view, ctx)
            self._drag_end(view, ctx)
        
        return True


if __name__ == '__main__':
    w = gtk.Window()
    w.connect('delete-event', gtk.main_quit)
    w.add(gtk.HBox(spacing=3))
    
    
    model = gtk.ListStore(str)
    for i in range(10): model.append(row=['Item%d' % i])
    treeview = DnDTreeView(model)
    treeview.set_model(model)
    crt = gtk.CellRendererText()
    col = gtk.TreeViewColumn("col1", crt, text=0)
    treeview.append_column(col)
    
    scroll = gtk.ScrolledWindow()
    scroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    scroll.add(treeview)
    
    w.child.pack_start(scroll)
    w.show_all()
    gtk.main()
