import gtk,  sys

class PyApp(gtk.Window):
    def __init__(self):
        super(PyApp,  self).__init__()
        
        self.set_title("Nueva ventana")
        self.set_size_request(250,  150) #dimensiones
        self.set_position(gtk.WIN_POS_CENTER) #posicion centrada
        
        try:
            self.set_icon_from_file("icono.ico") #icono de programa
        except Exception,  err:
                print err.message
                sys.exit(1)
                
        btn1 = gtk.Button("Boton1") #crear boton
        btn1.set_sensitive(False) #desactivado, no clickeable
        btn2 = gtk.Button("Boton2")
        btn3 = gtk.Button(stock=gtk.STOCK_CLOSE) #boton con imagen de cerrar
        btn4 = gtk.Button("Boton3")
        btn4.set_size_request(80,  40) #tamanio
        
        btn5 = gtk.Button("Tooltip")
        btn5.set_size_request(80,  35)
        
        self.fixed = gtk.Fixed() #contenedor de botones (widget contenedor de widgets hijos)
        
        self.fixed.put(btn1,  20,  30) #poner boton en contenedor + posicion (left, top)
        self.fixed.put(btn2,  100,  30)
        self.fixed.put(btn3,  20,  80)
        self.fixed.put(btn4,  100,  80)
        
        self.fixed.put(btn5,  100,  130)
        
        self.set_tooltip_text("window widget") #tooltip de la ventana
        btn5.set_tooltip_text("Button widget") #tooltip del boton 5
        
        self.connect("destroy",  gtk.main_quit) #destruir aplicacion al salir
        #self.show() #mostrar ventana
        self.add(self.fixed) #aniadir contenedor q sera la ventana principal
        self.show_all() #mostrar todos los widgets.
        
class PyLay(gtk.Window):
    def __init__(self):
        super(PyLay, self).__init__()
        
        self.set_title("ALineacion")
        self.set_size_request(260,  150)
        self.set_position(gtk.WIN_POS_CENTER)
        
        #contenedores
        vbox = gtk.VBox(False,  5)
        hbox = gtk.HBox(True,  3) #true = widgets en el area del mismo tamanio
        
        valign = gtk.Alignment(0,  1,  0,  0) #es un widget, izquierda, derecha, arriba, abajo. 1 = hacia la derecha
        vbox.pack_start(valign) #meter valign widget en vbox.
        
        ok = gtk.Button("OK")
        ok.set_size_request(70,  30)
        close = gtk.Button("Close")
        
        hbox.add(ok) #meter el widget-boton en el hbox
        hbox.add(close)
        
        halign = gtk.Alignment(1,  0,  0,  0)#alinear hacia la izquierda
        halign.add(hbox) #meter el contenedor hbox en el contenedor de alineacion
        
        vbox.pack_start(halign,  False,  False,  3)  #empacar-meter el contenedor de alineacion en el vbox
        
        #el ALineados solo puede contener un widget hijo, por eso se usan contenedores-boxes
        
        self.add(vbox)
        
        self.connect("destroy",  gtk.main_quit)
        self.show_all()
        



class PyTable(gtk.Window):
    
    def __init__(self):
        super(PyTable,  self).__init__()
        
        self.set_title("Calculator")
        self.set_size_request(250,  230)
        self.set_position(gtk.WIN_POS_CENTER)
        
        vbox = gtk.VBox(False,  2) #caja vertical, FAlse = widget dentro de distinto tamanio
        
        mb = gtk.MenuBar() #barra de menu
        filemenu = gtk.Menu() #menu (sera un submenu)
        filem = gtk.MenuItem("File") #elemento de la barra de menu
        filem.set_submenu(filemenu) #agregar submenu al elemento file
        mb.append(filem) #agregar el elmento con submenu a la barra de menu
        
        vbox.pack_start(mb,  False,  False,  0)
        
        table = gtk.Table(5,  4,  True) #tabla, filas, columnas, mismo tamanio (true) = al widget mas grande
        
        table.attach(gtk.Button("Cls"), 0, 1, 0, 1)
        table.attach(gtk.Button("Bck"), 1, 2, 0, 1)
        table.attach(gtk.Label(), 2, 3, 0, 1) #campo para escribir
        table.attach(gtk.Button("Close"), 3, 4, 0, 1)
        
        table.attach(gtk.Button("7"),  0,  1,  1,  2) #izq, der, arriba, abajo
        table.attach(gtk.Button("8"), 1, 2, 1, 2)
        table.attach(gtk.Button("9"), 2, 3, 1, 2)
        table.attach(gtk.Button("/"), 3, 4, 1, 2)

        table.attach(gtk.Button("4"), 0, 1, 2, 3)
        table.attach(gtk.Button("5"), 1, 2, 2, 3)
        table.attach(gtk.Button("6"), 2, 3, 2, 3)
        table.attach(gtk.Button("*"), 3, 4, 2, 3)

        table.attach(gtk.Button("1"), 0, 1, 3, 4)
        table.attach(gtk.Button("2"), 1, 2, 3, 4)
        table.attach(gtk.Button("3"), 2, 3, 3, 4)
        table.attach(gtk.Button("-"), 3, 4, 3, 4)

        table.attach(gtk.Button("0"), 0, 1, 4, 5)
        table.attach(gtk.Button("."), 1, 2, 4, 5)
        table.attach(gtk.Button("="), 2, 3, 4, 5)
        table.attach(gtk.Button("+"), 3, 4, 4, 5)
        
        vbox.pack_start(gtk.Entry(),   False,  False,  0)
        vbox.pack_end(table,  True,  True,  0) #empacar la tabla en la caja vertical
        
        self.add(vbox)
        self.show_all()
        


class PyWind(gtk.Window):
    
    def __init__(self):
        super(PyWind,  self).__init__()
        
        self.set_title("Windows")
        self.set_size_request(300,  250)
        self.set_border_width(8)
        self.set_position(gtk.WIN_POS_CENTER)
        
        table = gtk.Table(8,  4,  False) #8 filas 4 columnas, distinto tamanio depende del widget
        table.set_col_spacings(3) #espacio entre columnas 3px
        
        title = gtk.Label("Windows")
        
        halign = gtk.Alignment(0,  0,  0,  0)  #label alineado a la izquierda
        halign.add(title)
        
        table.attach(halign,  0,  1,  0,  1,  gtk.FILL, 
                            gtk.FILL,  0,  0) #poner label en la primer fila
        
        wins = gtk.TextView()
        wins.set_editable(False)
        wins.modify_fg(gtk.STATE_NORMAL,  gtk.gdk.Color(5140,  5140,  5140))
        wins.set_cursor_visible(False)
        table.attach(wins,  0,  2,  1,  3,  gtk.FILL | gtk.EXPAND, 
                           gtk.FILL | gtk.EXPAND,  1,  1) #expandir widget textview a dos columnas y dos filas
                           
        activate = gtk.Button("Activate")
        activate.set_size_request(50,  30)
        table.attach(activate,  3,  4,  1,  2,  gtk.FILL, 
                     gtk.SHRINK,  1,  1)
                     
        valign = gtk.Alignment(0,  0,  0,  0) #centrado
        close = gtk.Button("close")
        close.set_size_request(70,  30)
        valign.add(close)
        table.set_row_spacing(1,  3)
        table.attach(valign,  3,  4,  2,  3,  gtk.FILL, 
                     gtk.FILL | gtk.EXPAND,  1,  1)
                     
        halign2 = gtk.Alignment(0,  1,  0,  0)
        help = gtk.Button("Help")
        help.set_size_request(70,  30)
        halign2.add(help)
        table.set_row_spacing(3,  6)
        table.attach(halign2,  0,  1,  4,  5,  gtk.FILL, 
                     gtk.FILL,  0,  0)
                     
        ok = gtk.Button("ok")
        ok.set_size_request(70,  30)
        table.attach(ok,  3,  4,  4,  5,  gtk.FILL, 
                     gtk.FILL,  0,  0)
                     
        self.add(table)
        
        self.connect("destroy",  gtk.main_quit)
        self.show_all()
        
        
class PyBar(gtk.Window):
    
    def __init__(self):
        super(PyBar,  self).__init__()
        
        self.set_title("Toolbar")
        self.set_size_request(250, 200)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(6400, 6400, 6440))
        self.set_position(gtk.WIN_POS_CENTER)

        toolbar = gtk.Toolbar() #crear toolbar
        toolbar.set_style(gtk.TOOLBAR_ICONS) #solo iconos

        newtb = gtk.ToolButton(gtk.STOCK_NEW)
        opentb = gtk.ToolButton(gtk.STOCK_OPEN)
        savetb = gtk.ToolButton(gtk.STOCK_SAVE)
        sep = gtk.SeparatorToolItem() #separador
        quittb = gtk.ToolButton(gtk.STOCK_QUIT)
        
        quittb.connect("clicked", gtk.main_quit)

        toolbar.insert(newtb, 0) #insertar boton en el widget toolbar
        toolbar.insert(opentb, 1)
        toolbar.insert(savetb, 2)
        toolbar.insert(sep, 3)
        toolbar.insert(quittb, 4)

        vbox = gtk.VBox(False, 2)
        vbox.pack_start(toolbar, False, False, 0)

        self.add(vbox)

        self.connect("destroy", gtk.main_quit)
        self.show_all()


class PyBar2(gtk.Window):
    
    def __init__(self):
        super(PyBar2, self).__init__()

        self.set_title("Toolbar")
        self.set_size_request(250, 200)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(6440, 6440, 6440))
        self.set_position(gtk.WIN_POS_CENTER)
        
        self.count = 2

        toolbar = gtk.Toolbar()
        toolbar.set_style(gtk.TOOLBAR_ICONS)

        self.undo = gtk.ToolButton(gtk.STOCK_UNDO)
        self.redo = gtk.ToolButton(gtk.STOCK_REDO)
        sep = gtk.SeparatorToolItem()
        quit = gtk.ToolButton(gtk.STOCK_QUIT)

        toolbar.insert(self.undo, 0)
        toolbar.insert(self.redo, 1)
        toolbar.insert(sep, 2)
        toolbar.insert(quit, 3)
        
        self.undo.connect("clicked", self.on_undo)
        self.redo.connect("clicked", self.on_redo)
        quit.connect("clicked", gtk.main_quit)
        
        eve = gtk.EventBox() #para aniadir un color de background al toolbar, hay que meterlo en un eventbox.
        eve.add(toolbar)
        eve.modify_bg(gtk.STATE_NORMAL, None) #dejar con el color por defecto.

        vbox = gtk.VBox(False, 2)
        vbox.pack_start(eve, False, False, 0)

        self.add(vbox)

        self.connect("destroy", gtk.main_quit)
        self.show_all()
        
    def on_undo(self, widget):
        self.count = self.count - 1

        if self.count <= 0:
            self.undo.set_sensitive(False)
            self.redo.set_sensitive(True)


    def on_redo(self, widget):
        self.count = self.count + 1

        if self.count >= 5: 
            self.redo.set_sensitive(False)
            self.undo.set_sensitive(True)
            
            
            
class PySign(gtk.Window):
    def __init__(self):
        super(PySign, self).__init__()
        
        self.set_title("Quit Button")
        self.set_size_request(250, 200)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("destroy", self.on_destroy) #conectar(Senial, metodo)
        
        fixed = gtk.Fixed()

        quit = gtk.Button("Quit")
        quit.connect("clicked", self.on_clicked)
        quit.set_size_request(80, 35)

        fixed.put(quit, 50, 50)

        self.add(fixed)
        self.show_all()
        
    def on_destroy(self, widget):
        gtk.main_quit()
        
    def on_clicked(self, widget):
        gtk.main_quit()


        
import gobject

class PySign2(gtk.Window):
    """
    Objects in PyGTK may have predefined signal handlers.
    These handlers begin with do_*. For example do_expose(), do_show() or do_clicked(). 
    """
    __gsignals__ = {
        "configure-event" : "override" #sobre escribir handler (manejador) de senial do_configure-event por uno propio
        }

    def __init__(self):
        super(PySign2, self).__init__()

        self.set_size_request(200, 150)
        self.set_position(gtk.WIN_POS_CENTER)
       
        self.connect("destroy", gtk.main_quit)

        self.show_all()

    def do_configure_event(self, event):
        
        title = "%s, %s" % (event.x, event.y) #posicion en pantalla
        self.set_title(title)
        gtk.Window.do_configure_event(self, event) #llamada a super, no siempre necesaria

        
        
        
class PySignButton(gtk.Window):
    def __init__(self):
        super(PySignButton, self).__init__()
        
        self.set_title("Signals")
        self.set_size_request(250, 200)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("destroy", gtk.main_quit)
        
        fixed = gtk.Fixed()
        
        self.quit = gtk.Button("Quit")
        
        self.quit.connect("pressed", self.on_pressed) #registrar callbacks para seniales
        self.quit.connect("released", self.on_released)
        self.quit.connect("clicked", self.on_clicked)
        
        self.quit.set_size_request(80, 35)

        fixed.put(self.quit, 50, 50)
        
        self.add(fixed)
        self.show_all()
        self.emit_signal() #emitir al principio del programa senial para release del boton
        
    def emit_signal(self):
                
        event = gtk.gdk.Event(gtk.gdk.BUTTON_RELEASE)
        event.button = 1
        event.window = self.quit.window
        event.send_event = True
                
        self.quit.emit("button-release-event", event)
        
        
    def on_clicked(self, widget):
        print "clicked"
        
    def on_released(self, widget):
        print "released"
        
    def on_pressed(self, widget):
        print "pressed"
        



class PySignBlocked(gtk.Window):

    def __init__(self):
        super(PySignBlocked, self).__init__()

        self.set_title("Blocking a callback")
        self.set_size_request(250, 180)
        self.set_position(gtk.WIN_POS_CENTER)
        
        fixed = gtk.Fixed()
        button = gtk.Button("Click")
        button.set_size_request(80, 35)
        self.id = button.connect("clicked", self.on_clicked) #connect devuelve un id que se puede usar para bloquear la senial
        fixed.put(button, 30, 50)

        check = gtk.CheckButton("Connect") #boton de check
        check.set_active(True) #activo por defecto
        check.connect("clicked", self.toggle_blocking, button) #conectar senial clicked con el metodo handler, pasar el boton o widget a bloquear
        fixed.put(check, 130, 50)


        self.connect("destroy", gtk.main_quit)

        self.add(fixed)
        self.show_all()

    def on_clicked(self, widget): #metodo handler
        print "clicked"

    def toggle_blocking(self, checkbox, button):
        if checkbox.get_active(): #si esta activo el chek_box desbloquear
           button.handler_unblock(self.id)
        else:
           button.handler_block(self.id)



class PyMsg(gtk.Window): 
    def __init__(self):
        super(PyMsg, self).__init__()
        
        self.set_size_request(250, 100)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("destroy", gtk.main_quit)
        self.set_title("Message dialogs")
        
        
        table = gtk.Table(2, 2, True);
        
        info = gtk.Button("Information")
        warn = gtk.Button("Warning")
        ques = gtk.Button("Question")
        erro = gtk.Button("Error")

        
        info.connect("clicked", self.on_info)
        warn.connect("clicked", self.on_warn)
        ques.connect("clicked", self.on_ques)
        erro.connect("clicked", self.on_erro)
        
        table.attach(info, 0, 1, 0, 1)
        table.attach(warn, 1, 2, 0, 1)
        table.attach(ques, 0, 1, 1, 2)
        table.attach(erro, 1, 2, 1, 2)
        
        
        self.add(table)
        self.show_all()

    def on_info(self, widget):
        md = gtk.MessageDialog(self, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, 
            gtk.BUTTONS_CLOSE, "Download completed") #gtk.MESSAGE_INFO = tipo de mensaje.
        md.run() #mostrar dialogo
        md.destroy()
        
    
    def on_erro(self, widget):
        md = gtk.MessageDialog(self, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, 
            gtk.BUTTONS_CLOSE, "Error loading file")
        md.run()
        md.destroy()
    
    
    
    def on_ques(self, widget):
        md = gtk.MessageDialog(self, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, 
            gtk.BUTTONS_CLOSE, "Are you sure to quit?")
        md.run()
        md.destroy()
    
    
    def on_warn(self, widget):
        md = gtk.MessageDialog(self, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, 
            gtk.BUTTONS_CLOSE, "Unallowed operation")
        md.run()
        md.destroy()

        
        
        
        
        

PyMsg()
#PySignBlocked()
#PySignButton()
#PySign2()
#PyBar2()
#PyWind()
#PyTable()
#PyLay()
#PyApp()
gtk.main()
