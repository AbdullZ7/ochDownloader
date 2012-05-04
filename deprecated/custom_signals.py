import time
import pygtk
import gobject

#from core.events import Events


#DEPRECATED
class CaptchaSig(gobject.GObject):
    """
    
    DEPRECATED
    
    Custom events: pygtk.org/articles/subclassing-gobject/sub-classing-gobject-in-python.htm
    Model view controller philosophy.
    """
    #set properties
    __gproperties__ = {
                       'dialog': (gobject.TYPE_PYOBJECT,   #type
                                  "captcha dialog",              #nick name
                                  "text box to complete",     #description
                                  gobject.PARAM_READWRITE
                                  ),
                        'solution': (gobject.TYPE_STRING,   #type
                                  "input solution",                   #nick name
                                  "captcha input solution",     #description
                                  None,                                       #default value
                                  gobject.PARAM_READWRITE
                                  ), 
                        'done': (gobject.TYPE_BOOLEAN,   #type
                                  "all done flag",              #nick name
                                  "wait until flag = True",     #description
                                  False,                                    #default value
                                  gobject.PARAM_READWRITE
                                  ),
                       }
    
    #set signals
    __gsignals__ = {
                    'captcha-dialog': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_STRING, #tipo de retorno (none = no retorna nada)
                                       (gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)                                                      #parametros (respectivos a propiedades)
                                       )
                    }
    
    def __init__(self, captcha_dlg):
        """"""
        gobject.GObject.__init__(self) #register properties and signals
        self.dialog = captcha_dlg #property: captcha_dlg_gui.py
        self.solution = None
        self.done = False
    
    def do_get_property(self, property):
        if property.name == "dialog":
            return self.dialog
        else:
            raise AttributeError, "unknown property: {0}".format(property.name)
    
    def do_set_property(self, property, value):
        if property.name == "solution":
            self.solution = value
        elif property.name == "done":
            self.done = value
        else:
            raise AttributeError, "unknown property: {0}".format(property.name)
    
    def reset_default(self):
        self.solution = None
        self.done = False
    
    #def do_captcha_dialog(self, captcha_dlg=None): #called after emit signal retun.
    
    def start(self, service, get_captcha_img, set_solution):
        """
        Signal emition is supposed to be started from separated threads.
        """
        self.reset_default()
        #start emition on the main gtk loop (idle_add...). Otherwise it will hang in Windows.
        gobject.idle_add(self.emit, 'captcha-dialog', self.dialog, service, get_captcha_img) #get_property = returned widget/obj.
        while True:
            if self.done:
                break
            time.sleep(1)
        
        set_solution(self.solution) #recaptcha.py method.
    
gobject.type_register(CaptchaSig) #registrar como GType para poder usarse.


class ChangeIPSig(gobject.GObject):
    """
    Custom events: pygtk.org/articles/subclassing-gobject/sub-classing-gobject-in-python.htm
    Model view controller philosophy.
    """
    #set properties
    __gproperties__ = {
                        'changing-flag': (gobject.TYPE_BOOLEAN,   #type
                                  "ip change flag",              #nick name
                                  "ip change in progress",     #description
                                  False,                                    #default value
                                  gobject.PARAM_READWRITE
                                  ),
                       }
    
    #set signals
    __gsignals__ = {
                    'change-ip': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_STRING, #tipo de retorno (none = no retorna nada)
                                       (gobject.TYPE_PYOBJECT, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)                                                      #parametros (respectivos a propiedades)
                                       )
                    }
    
    def __init__(self):
        """"""
        gobject.GObject.__init__(self) #register properties and signals
        self.changing_flag = False
    
    def do_set_property(self, property, value):
        if property.name == "changing-flag":
            self.changing_flag = value
        else:
            raise AttributeError, "unknown property: {0}".format(property.name)
    
    #def do_captcha_dialog(self, captcha_dlg=None): #called after emit signal retun.
    
    def start(self, service, get_captcha_img):
        """
        Signal emition is supposed to be started from separated threads.
        """
        if not self.changing_flag:
            self.changing_flag = True
            #start emition on the main gtk loop (idle_add...). Otherwise it will hang in Windows.
            gobject.idle_add(self.emit, 'change-ip') #get_property = returned widget/obj.
    
gobject.type_register(ChangeIPSig) #registrar como GType para poder usarse.
