import sqlite3


class UseDataBase:

    def __init__(self):
        self._db = 'app/models/v_stravy.db'

    def __enter__(self):
        self.conn = sqlite3.connect(self._db)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, ecx_value, exc_trace):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
