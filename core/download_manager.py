import os
import threading
import logging
logger = logging.getLogger(__name__)

import cons
import events
from download_core import DownloadCore
from thread_manager import ThreadManager
from slots import Slots
from host_accounts import host_accounts
from conf_parser import conf
from core.plugin.parser import plugins_parser


class DownloadManager(DownloadCore, ThreadManager):
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
        DownloadCore.__init__(self) #download_core.py
        ThreadManager.__init__(self) #thread_manager.py
        self.global_slots = Slots() #slots.py
    
    def start_all(self, id_order_list):
        """"""
        self.queue_downloads.update(self.stopped_downloads)
        self.stopped_downloads.clear()
        self.reorder_queue(id_order_list)
        self.next_download()
    
    def stop_all(self):
        """"""
        for id_item, download_item in self.active_downloads.iteritems():
            self.stop_thread(id_item)
        for id_item, download_item in self.queue_downloads.items():
            self.stopped_downloads[id_item] = download_item
            del self.queue_downloads[id_item]

    def start_download(self, id_item):
        """"""
        try:
            download_item = self.stopped_downloads.pop(id_item)
        except KeyError:
            return False
        else:
            self.queue_downloads[id_item] = download_item
            self.next_download()
            return True

    def stop_download(self, id_item):
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
        else: # active
            self.stop_thread(id_item)
            return True

    def delete_download(self, id_items_list, remove_file=False):
        """"""
        for id_item in id_items_list:
            th = None
            try:
                download_item = self.active_downloads.pop(id_item)
            except KeyError:
                try:
                    download_item = self.stopped_downloads.pop(id_item)
                except KeyError:
                    try:
                        download_item = self.queue_downloads.pop(id_item)
                    except KeyError:
                        try:
                            download_item = self.complete_downloads.pop(id_item)
                        except KeyError:
                            raise
            else: # active
                th = self.get_thread(id_item)
                self.stop_thread(id_item)
                self.delete_thread(id_item)
                self.global_slots.remove_slot()
                self.next_download()

            if remove_file:
                threading.Thread(group=None, target=self.remove_file, name=None, args=(download_item, th)).start()

    def remove_file(self, download_item, th):
        """"""
        if th is not None:
            th.join()
        try:
            os.remove(os.path.join(download_item.path, download_item.name))
        except Exception as err:
            logger.warning(err)

    def update_active_downloads(self):
        """
        Roba ciclos.
        This may change the active_downloads dict, you should get a dict copy before calling this method.
        """
        for id_item, download_item in self.active_downloads.items():
            item_data = self.get_thread_update(id_item) #threadmanager
            download_item.update(*item_data)
            limit_exceeded = self.is_limit_exceeded(id_item) #threadmanager
            old_status = download_item.status
            if old_status in (cons.STATUS_STOPPED, cons.STATUS_FINISHED, cons.STATUS_ERROR):
                if old_status == cons.STATUS_STOPPED:
                    self.stopped_downloads[id_item] = download_item
                elif old_status == cons.STATUS_FINISHED:
                    self.complete_downloads[id_item] = download_item
                else: #status == cons.STATUS_ERROR
                    download_item.fail_count += 1
                    if download_item.fail_count > conf.get_retries_limit():
                        download_item.status = cons.STATUS_STOPPED
                        self.stopped_downloads[id_item] = download_item
                    else:
                        download_item.status = cons.STATUS_QUEUE
                        self.queue_downloads[id_item] = download_item
                self.delete_thread(id_item) #threadmanager
                del self.active_downloads[id_item]
                self.global_slots.remove_slot()
                self.next_download()
                if old_status == cons.STATUS_FINISHED:
                    events.download_complete.emit(download_item)
                if not self.active_downloads and old_status != cons.STATUS_STOPPED:
                    events.all_downloads_complete.emit()
                if limit_exceeded and self.active_downloads and old_status == cons.STATUS_ERROR:
                    events.limit_exceeded.emit()

    def update_download_item(self, download_item):
        pass

    def downloader_init(self, item_list, path):
        """
        Crea los threads para la descarga de cada archivo.
        """
        #if not self.active_downloads: #after this method completes, there will be one active download at least.
            #events.trigger_downloading_process_pre_start()
        for download_item in item_list:
            download_item.path = path
            self.queue_downloads[download_item.id] = download_item
        self.next_download()

    def next_download(self):
        for download_item in self.queue_downloads.values():
            started = self.download_starter(download_item)
            if not started:
                break

    def download_starter(self, download_item):
        """"""
        if not self.global_slots.available_slot():
            return False
        elif not self.is_host_slot_available(download_item.host) and host_accounts.get_account(download_item.host) is None: # not premium.
            return False
        else:
            download_item.fail_count = 0
            self.global_slots.add_slot()
            self.create_thread(download_item) #threadmanager
            self.active_downloads[download_item.id] = download_item
            del self.queue_downloads[download_item.id]
            return True

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
