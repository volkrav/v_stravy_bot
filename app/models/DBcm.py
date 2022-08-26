import sqlite3 as sq



class UseDataBase:

    # def __init__(self, config: str) -> None:
    #     self.configuration = config

    async def __aenter__(self) -> 'cursor':
        self.conn = sq.connect('app/models/v_stravy.db')
        self.cursor = self.conn.cursor()
        return self.cursor

    async def __aexit__(self, exc_type, ecx_value, exc_trace) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
