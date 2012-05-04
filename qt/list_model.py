
from PySide.QtGui import *
from PySide.QtCore import *


class SimpleListModel(QAbstractItemModel):
    def __init__(self, headers, items, bool_cols=None):
        QAbstractItemModel.__init__(self)
        #self.setSupportedDragActions(Qt.MoveAction)
        self.__bool_cols = bool_cols or []
        self.__items = items #or [] wont keep the binding to the same list when its empty.
        self.__headers = headers

    #Reimplemented virtual functions below.
    def rowCount(self, parent=QModelIndex()):
        if parent == QModelIndex():
            return len(self.__items)
        #elif parent.isValid():
            #return False
        else:
            return 0
    
    def data(self, index, role=Qt.DisplayRole):
        """
        index: QModelIndex
        Returns the data stored under the given role
        for the item referred to by the index.
        """
        if not index.isValid():
            return None
        elif index.column() in self.__bool_cols:
            if role == Qt.CheckStateRole:
                row = self.__items[index.row()]
                item = row[index.column()] #index = iter
                value = Qt.Checked if item else Qt.Unchecked
                return value
            else:
                return None
        elif role == Qt.DisplayRole:
            row = self.__items[index.row()]
            #return index.internalPointer()[index.column()]
            return row[index.column()] #index = iter
        else:
            return None
    
    def setData(self, index, value, role=Qt.EditRole):
        """
        index: QModelIndex
        """
        if not index.isValid():
            return False
        elif index.column() in self.__bool_cols and role == Qt.CheckStateRole:
            item = True if value == Qt.Checked else False
            row = self.__items[index.row()]
            row[index.column()] = item
            self.dataChanged.emit(index, index)
            return True
        #elif role == Qt.EditRole:
            #row = self.__items[index.row()]
            #row[index.column()] = value
            #self.dataChanged.emit(index, index)
            #return True
        else:
            return False
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        elif index.column() in self.__bool_cols:
            return Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled #| Qt.ItemIsEditable
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
            returns column header title
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.__headers[section]
        return None
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.__headers)
    
    def index(self, row, column=1, parent=QModelIndex()):
        """
        Returns the index of the item in the model
        specified by the given row, column and parent index.
        """
        if parent == QModelIndex() and row < len(self.__items):
            pointer = self.__items[row]
            index = self.createIndex(row, column, pointer)
        else:
            index = QModelIndex()
        return index
    
    def parent(self, child):
        return QModelIndex()
    
    def supportedDropActions(self):
        return Qt.MoveAction #| Qt.CopyAction
    
    def clear(self):
        self.beginRemoveRows(QModelIndex(), 0, len(self.__items) - 1)
        del self.__items[:]
        self.endRemoveRows()
    
    def remove(self, row):
        self.beginRemoveRows(QModelIndex(), row, row) #parent, first, last
        del self.__items[row]
        self.endRemoveRows()
    
    def insert(self, index, item):
        self.beginInsertRows(QModelIndex(), index, index)
        self.__items.insert(index, item)
        self.endInsertRows()
    
    def append(self, item):
        self.beginInsertRows(QModelIndex(), len(self.__items), len(self.__items))
        self.__items.append(item)
        self.endInsertRows()
    
    def refresh(self):
        #better way?
        if self.__items:
            #first_index = self.index(0, 0)
            #last_index = self.index(len(self.__items) - 1, len(self.__headers) - 1)
            self.dataChanged.emit(QModelIndex(), QModelIndex())





