class Tree(gtk.VBox):
	"""
    Arbol de archivos descargando.
    """
	def __init__(self, get_files):
		""""""
		gtk.VBox.__init__(self)
		scroll = gtk.ScrolledWindow()
		scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        #TreeStore(icon, status, path, name, progress(int), progress_visible(bool), current_size, total_size, speed, time, services)
		self.treeview = gtk.TreeView(gtk.TreeStore(gtk.gdk.Pixbuf, str, str, str, int, bool, str, str, str, str, str))
		scroll.add(self.treeview)
		self.pack_start(scroll)

		self.get_files = get_files

		self.treeview.set_rules_hint(True)
		self.treeview.set_headers_visible(False)
		
		#tree columns
		tree_icon = gtk.TreeViewColumn('Icon') 
		icon_cell = gtk.CellRendererPixbuf()
		tree_icon.pack_start(icon_cell, False)
		tree_icon.add_attribute(icon_cell, 'pixbuf', 0)
		self.treeview.append_column(tree_icon)
				  
		tree_name = gtk.TreeViewColumn('Name')
		tree_name.set_max_width(350)
		name_cell = gtk.CellRendererText()
		tree_name.pack_start(name_cell, True)
		tree_name.add_attribute(name_cell, 'text', 3)
		self.treeview.append_column(tree_name)
		
		tree_progress = gtk.TreeViewColumn('Progress')
		tree_progress.set_min_width(150)
		progress_cell = gtk.CellRendererProgress()
		tree_progress.pack_start(progress_cell, True)
		tree_progress.add_attribute(progress_cell, 'value', 4)
		tree_progress.add_attribute(progress_cell, 'visible', 5)
		self.treeview.append_column(tree_progress)
		
		tree_current_size = gtk.TreeViewColumn('Current Size')
		current_size_cell = gtk.CellRendererText()
		tree_current_size.pack_start(current_size_cell, False)
		tree_current_size.add_attribute(current_size_cell, 'text', 6)
		self.treeview.append_column(tree_current_size)

		tree_total_size = gtk.TreeViewColumn('Total Size')
		total_size_cell = gtk.CellRendererText()
		tree_total_size.pack_start(total_size_cell, False)
		tree_total_size.add_attribute(total_size_cell, 'text', 7)
		self.treeview.append_column(tree_total_size)
		
		tree_speed = gtk.TreeViewColumn('Speed')
		speed_cell = gtk.CellRendererText()
		tree_speed.pack_start(speed_cell, False)
		tree_speed.add_attribute(speed_cell, 'text', 8)
		self.treeview.append_column(tree_speed)
		
		tree_time = gtk.TreeViewColumn('Time Left')
		time_cell = gtk.CellRendererText()
		tree_time.pack_start(time_cell, False)
		tree_time.add_attribute(time_cell, 'text', 9)
		self.treeview.append_column(tree_time)
		
		tree_plugins = gtk.TreeViewColumn('Plugin')
		plugins_cell = gtk.CellRendererText()
		tree_plugins.pack_start(plugins_cell, False)
		tree_plugins.add_attribute(plugins_cell, 'text', 10)
		self.treeview.append_column(tree_plugins)
		
		#icons
		self.package_icon = self.treeview.render_icon(gtk.STOCK_OPEN, gtk.ICON_SIZE_MENU)
		self.active_service_icon = self.treeview.render_icon(gtk.STOCK_YES, gtk.ICON_SIZE_MENU)
		self.unactive_service_icon = self.treeview.render_icon(gtk.STOCK_NO, gtk.ICON_SIZE_MENU)
		self.correct_icon = self.treeview.render_icon(gtk.STOCK_APPLY, gtk.ICON_SIZE_MENU)
		self.failed_icon = self.treeview.render_icon(gtk.STOCK_CANCEL, gtk.ICON_SIZE_MENU)
		self.wait_icon = self.treeview.render_icon(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU)
		self.active_icon = self.treeview.render_icon(gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_MENU)
		self.pending_icon = self.treeview.render_icon(gtk.STOCK_MEDIA_PAUSE, gtk.ICON_SIZE_MENU)
		self.stoped_icon = self.treeview.render_icon(gtk.STOCK_MEDIA_STOP, gtk.ICON_SIZE_MENU)
		self.icons = {"Correct": self.correct_icon, "Error": self.failed_icon, "Wait": self.wait_icon, "Active": self.active_icon, "Pending": self.pending_icon, "Stop": self.stoped_icon}
		
        #Status bar de abajo.
		self.status_bar = gtk.Statusbar()
		self.status_bar.set_has_resize_grip(False)
		self.pack_start(self.status_bar, False)
		self.status_bar.push(self.status_bar.get_context_id(""), "\t" + "No Downloads Active.")
		self.updating = False
