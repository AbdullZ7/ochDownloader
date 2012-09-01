import os #usado en FileHandler
import threading
import importlib
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).
from collections import OrderedDict

import cons
import misc #(html entities and numerics parser)
from download_core import DownloadItem
from slots import Slots


class AddDownloadsManager:
    """"""
    def __init__(self):
        """
        DONE: Cambiar listas por diccionarios {id_item: downloaditem, } para simplificar busquedas.
        """
        self.__slots = Slots(limit=20) #checker stots
        self.__pending_downloads = OrderedDict() #{id_item: download_item, }
        self.__checking_downloads = {} #{id_item: download_item, }
        self.__ready_downloads = {} #{id_item: download_item, } checked_downloads
        self.__thread_checking_downloads = {} #{id_item: th, }

    def clear_pending(self):
        """
        Erase pending_downloads dicts
        """
        self.__pending_downloads.clear()
        self.__checking_downloads.clear()
        self.__ready_downloads.clear()
        self.__slots.set_slots(slots=0)

    def create_download_item(self, file_name, size, link, copy_link=True):
        """"""
        host = misc.get_host(link)
        download_item = DownloadItem(file_name, host, size, link, can_copy_link=copy_link)
        self.__pending_downloads[download_item.id] = download_item
        return download_item
    
    def start_checking(self):
        """"""
        for id_item, download_item in self.__pending_downloads.items(): #devuelve lista con key, values
            if self.__slots.add_slot():
                self.__checking_downloads[id_item] = download_item
                del self.__pending_downloads[id_item]
                th = threading.Thread(group=None, target=self.plugin_link_checking, name=None, args=(download_item, ))
                self.__thread_checking_downloads[id_item] = th
                #th.daemon = True #quit thread on exit.
                th.start()
            else:
                break
    
    def plugin_link_checking(self, download_item): #link_checking
        """
        TODO: crear modulos multi_link_checker para los host
        que permiten chequear varios links en un solo pedido.
        TODO: crear en clase con atrubutos file_name, etc. asi actualizar
        desde el update checking solo si aun esta en una lista.
        """
        #host = download_item.host
        link_status = cons.LINK_CHECKING
        size = 0
        status_msg = None
        file_name = None
        try:
            module = importlib.import_module("plugins.{0}.link_checker".format(download_item.host))
        except ImportError as err:
            logger.info(err)
            file_name = misc.get_filename_from_url(download_item.link) or cons.UNKNOWN #may be an empty str
            link_status, download_item.host = cons.LINK_ERROR, cons.UNSUPPORTED
        except Exception as err:
            logger.exception(err)
            link_status, download_item.host = cons.LINK_ERROR, cons.UNSUPPORTED
        else:
            link_status, file_name, size, status_msg = module.LinkChecker().check(download_item.link)
        finally: #update items attributes. TODO: create a method to update all of them.
            #atomic stuff.
            download_item.link_status = link_status
            download_item.size = size
            download_item.link_status_msg = status_msg
            if file_name is not None:
                file_name = misc.smartdecode(misc.html_entities_parser(file_name))
                if download_item.name == cons.UNKNOWN: #may be downloading
                    download_item.name = file_name #smartdecode return utf-8 string
    
    def get_checking_update(self):
        """"""
        result_list = []
        for id_item, download_item in self.__checking_downloads.items():
            result_list.append(download_item)
            th = self.__thread_checking_downloads[id_item]
            if not th.is_alive():
                self.__ready_downloads[id_item] = download_item
                del self.__checking_downloads[id_item]
                del self.__thread_checking_downloads[id_item]
                self.__slots.remove_slot()
                self.start_checking()
        return result_list
    
    def recheck_items(self):
        """"""
        for id_item, download_item in self.__ready_downloads.items():
            if download_item.link_status not in (cons.LINK_CHECKING, cons.LINK_ALIVE):
                download_item.link_status = cons.LINK_CHECKING #safe
                self.__pending_downloads[id_item] = download_item
                del self.__ready_downloads[id_item]
                self.start_checking()
                #threading.Thread(group=None, target=self.plugin_link_checking, name=None, args=(download_item, )).start() #safe

    def get_added_items(self, id_add_list): #get download_items (added) from pending.
        """"""
        result_list = []
        for id_item in id_add_list: #add this items.
            try:
                download_item = self.__checking_downloads.pop(id_item)
                del self.__thread_checking_downloads[id_item]
                self.__slots.remove_slot()
            except:
                try:
                    download_item = self.__ready_downloads.pop(id_item)
                except:
                    try:
                        download_item = self.__pending_downloads.pop(id_item) #so we only keep the non-added items in the pending_dict
                    except Exception as err:
                        download_item = None
                        logger.warning(err)
                
            if download_item is not None:
                result_list.append(download_item)
            
        return result_list

