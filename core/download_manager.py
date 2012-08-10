import os #usado en FileHandler
import importlib
import threading
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

import cons
from misc import html_entities_parser, smartdecode #(html entities and numerics parser)
from download_core import DownloadCore, DownloadItem
from thread_manager import ThreadManager
from add_downloads_manager import AddDownloadsManager
from slots import Slots
from host_accounts import host_accounts
from conf_parser import conf
from plugins_parser import plugins_parser
from events import events


class DownloadManager(DownloadCore, ThreadManager): #herencia multiple
    """
    DownloadCore:
    .Contiene las listas con los items (tipos de clase, DownloadItem) de descarga, y los metodos para modificar esas listas.
    .Atributos heredados:
    self.active_downloads, self.queue_downloads, self.complete_downloads, self.stopped_downloads
    .Metodos heredados:
    -
    
    ThreadManager:
    .Contiene el diccionario con los threads (de descarga, clase Downloader) instanciados de las descargas activas.
    .Atributos heredados:
    self.thread_downloads (DICT)
    .Metodos heredados:
    get_thread, add_thread, delete_thread, stop_thread, stop_all, get_thread_status
    """
    def __init__(self):
        """"""
        DownloadCore.__init__(self) #inicializar download_core.py
        ThreadManager.__init__(self) #inicializar thread_manager.py
        self.global_slots = Slots() #slots.py
    
    def start_all(self, id_order_list):
        """"""
        self.queue_downloads.update(self.stopped_downloads)
        self.stopped_downloads.clear()
        self.reorder_queue(id_order_list)
        for download_item in self.queue_downloads.values():
            download_item.reset_fail_count()
            self.download_starter(download_item)
    
    def stop_all(self, filter_host_list=None):
        """"""
        if filter_host_list is None:
            filter_host_list = []
        for id_item, download_item in self.active_downloads.iteritems():
            if download_item.host not in filter_host_list:
                self.stop_thread(self.get_thread(id_item))
        for id_item, download_item in self.queue_downloads.items():
            if download_item.host not in filter_host_list:
                self.stopped_downloads[id_item] = download_item
                del self.queue_downloads[id_item]

    def start_download(self, id_item): #iniciar descarga. Boton play.
        """"""
        try:
            download_item = self.stopped_downloads.pop(id_item)
        except KeyError:
            return False
        else:
            self.downloader_init([download_item, ], download_item.path)
            return True

    def stop_download(self, id_item): #detener descarga. Boton stop.
        """"""
        try:
            download_item = self.active_downloads[id_item]
        except KeyError:
            try:
                download_item = self.queue_downloads.pop(id_item)
                self.stopped_downloads[id_item] = download_item
            except KeyError:
                return False
            else:
                return True
        else:
            self.stop_thread(self.get_thread(id_item))
            return True

    def delete_download(self, id_items_list):
        """"""
        for id_item in id_items_list:
            is_active = False
            try:
                download_item = self.active_downloads.pop(id_item)
                is_active = True
            except KeyError:
                try:
                    download_item = self.stopped_downloads.pop(id_item)
                except KeyError:
                    try:
                        download_item = self.queue_downloads.pop(id_item)
                    except KeyError as err: #will crash after this and that's ok.
                        logger.exception(err)
            th = None
            if is_active:
                th = self.get_thread(id_item)
                self.stop_thread(th)
                self.delete_thread(id_item)
                self.global_slots.remove_slot()
                self.next_download()
                
            threading.Thread(group=None, target=self.remove_file, name=None, args=(download_item, th)).start()

    def remove_file(self, download_item, th):
        """"""
        if th is not None:
            th.join()
        try:
            os.remove(os.path.join(download_item.path, download_item.name))
        except EnvironmentError as err:
            logger.warning(err)

    def get_items_update(self):
        """
        Roba ciclos.
        """
        result_list = []
        for id_item, download_item in self.active_downloads.items():
            item_data = self.get_thread_status(id_item) #Metodo de threadManager heredado
            if item_data is not None:
                download_item.update(*item_data)
                limit_exceeded = self.is_limit_exceeded(download_item.id)
            else:
                download_item.status = cons.STATUS_ERROR
                limit_exceeded = False
            status = download_item.status
            result_list.append(download_item)
            if status in (cons.STATUS_STOPPED, cons.STATUS_FINISHED, cons.STATUS_ERROR):
                if status == cons.STATUS_FINISHED:
                    self.complete_downloads[id_item] = download_item
                elif status == cons.STATUS_ERROR:
                    logger.warning("status error: {0}".format(download_item.host))
                    download_item.fail_count += 1
                    if download_item.fail_count > conf.get_retries_limit():
                        download_item.status = cons.STATUS_STOPPED
                        self.stopped_downloads[id_item] = download_item
                    else:
                        download_item.status = cons.STATUS_QUEUE
                        self.queue_downloads[id_item] = download_item
                else: #stopped
                    self.stopped_downloads[id_item] = download_item
                self.delete_thread(id_item) #metodo de threadmanager heredado
                del self.active_downloads[id_item]
                self.global_slots.remove_slot() #remove the slot, so the next download can start.
                self.next_download()
                if status == cons.STATUS_FINISHED:
                    events.trigger_download_complete(download_item)
                if not (self.active_downloads or self.queue_downloads) and status != cons.STATUS_STOPPED:
                    events.trigger_all_downloads_complete()
                elif limit_exceeded: #cons.STATUS_ERROR
                    events.trigger_limit_exceeded()
        
        return result_list

    def downloader_init(self, item_list, save_to_path): #start_thread. Crea el thread para el link dado.
        """
        Crea los threads para la descarga de cada archivo.
        """
        #if not self.active_downloads: #after this method completes, there will be one active download at least.
            #events.trigger_downloading_process_started()
        for download_item in item_list: #in self.pending_downloads:
            download_item.set_path(save_to_path)
            download_item.reset_fail_count()
            self.queue_downloads[download_item.id] = download_item
            self.download_starter(download_item)

    def next_download(self):
        """
        Init next download on queue. This is called when an active download is stopped or has finished.
        """
        for download_item in self.queue_downloads.values(): #iniciar la proxima descarga en la cola, o la proxima...
            if self.global_slots.available_slot():
                self.download_starter(download_item) #iniciar descarga si es posible (si ya no se esta bajando del mismo host)
            else:
                break

    def download_starter(self, download_item):
        """"""
        if self.global_slots.available_slot():
            slot = True
            if host_accounts.get_account(download_item.host) is None: #si no es premium entrar.
                if not self.is_host_slot_available(download_item.host):
                    slot = False
            if slot:
                self.global_slots.add_slot()
                self.add_thread(download_item.id, download_item.name, download_item.path, download_item.link, download_item.host, download_item.chunks) #crear thread y comenzar descarga. Metodo de threadmanager heredado
                self.active_downloads[download_item.id] = download_item
                del self.queue_downloads[download_item.id]

    def is_host_slot_available(self, host):
        """"""
        count = 0
        host_slots = plugins_parser.get_plugin_item(host).get_slots_limit()
        if host_slots > 0: #-1 or 0 means unlimited slots
            for download_item in self.active_downloads.itervalues():
                if host == download_item.host:
                    count += 1
                if count >= host_slots:
                    return False
        return True

    def new_slot_limit(self, new_limit):
        """"""
        current_limit = self.global_slots.get_limit()
        self.global_slots.set_limit(new_limit)
        if new_limit > current_limit:
            self.next_download()


if __name__ == "__main__":
    pass
