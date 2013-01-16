# -*- coding: utf-8 -*-
__author__ = 'Esteban Castro Borsani'


class UnRARError(Exception): pass

class BadHeaderData(UnRARError): pass
class BadPassword(UnRARError): pass
class InvalidArchive(UnRARError): pass
class ArchiveOpenError(UnRARError): pass
class EndOfArchive(UnRARError): pass
class ReadError(UnRARError): pass
class CloseError(UnRARError): pass