import sqlite3
import os
import datetime
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).


import core.cons as cons


class History:
    """"""
    def __init__(self):
        """"""
        try:
            if not os.path.exists(cons.DB_PATH):
                os.makedirs(cons.DB_PATH)
        except EnvironmentError as err:
            logger.exception(err)
        
        self.conn = sqlite3.connect(cons.DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
        self.create_db()
    
    def create_db(self):
        """"""
        try:
            with self.conn:
                self.conn.execute("""create table history (
                                                id integer primary key,
                                                file_name varchar(255) not null,
                                                link varchar(255),
                                                size integer not null,
                                                complete integer not null,
                                                path varchar(255) not null,
                                                insert_date timestamp not null
                                                )""")
        except sqlite3.OperationalError as err:
            logger.debug(err)
    
    def get_data(self, offset, limit=50, match_term=""):
        """"""
        try:
            cur = self.conn.cursor()
            if match_term:
                self._get_match_data_query(cur, offset, limit, match_term)
            else:
                self._get_data_query(cur, offset, limit)
            data_list = [row for row in cur]
            #for row in cur: #tuple
                #print "{0} {1} {2} {3}".format(id, name, host, date.strftime("%d-%m-%y %H:%M"))
        except sqlite3.OperationalError as err:
            logger.debug(err)
            return []
        else:
            return data_list
    
    def _get_data_query(self, cur, offset, limit):
        """"""
        cur.execute("""SELECT * FROM history
                            ORDER BY id DESC
                            LIMIT :limit
                            OFFSET :offset""",
                            {"limit": limit, "offset": offset}
                            )
    
    def _get_match_data_query(self, cur, offset, limit, match_term):
        """"""
        match_term = '%' + match_term.replace(" ", '%') + '%' #% = wildcares, (such as *)
        cur.execute("""SELECT * FROM history
                            WHERE file_name LIKE LOWER(:match_term)
                            ORDER BY id DESC
                            LIMIT :limit
                            OFFSET :offset""",
                            {"limit": limit, "offset": offset, "match_term": match_term}
                            )
    
    def set_values(self, name, link, size, complete, path):
        """"""
        try:
            with self.conn:
                self.conn.execute("INSERT INTO history(file_name, link, size, complete, path, insert_date) VALUES (:name, :link, :size, :complete, :path, :date)",
                                            {"name": name, "link": link, "size": size, "complete": complete, "path": path, "date": datetime.datetime.now()})
        except sqlite3.OperationalError as err:
            logger.debug(err)


if __name__ == "__main__":
    h = History()
    for num in range(53):
        h.set_values("example_soma"+str(num), None, 50000000, 50, "C:\\dir")
    print h.get_data(0)
    #print [row for row in cur]
    print "done"

