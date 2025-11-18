
import collections
import sys, sqlite3

class Repository:

    def __init__(self, db):
        self.db = db

    @classmethod
    def open(cls, path):
        schema = ['''
            PRAGMA foreign_keys = ON''', '''
            CREATE TABLE IF NOT EXISTS "log" (
                "id"        INTEGER PRIMARY KEY,
                "address"   TEXT NOT NULL,
                "metric"    TEXT NOT NULL,
                "value"     REAL,
                "timestamp" INTEGER NOT NULL
            ) STRICT''']

        db = sqlite3.connect(path)
        cursor = db.cursor()
        for statment in schema:
            cursor.execute(statment)

        def named_rows(cursor, row):
            fields = [col[0] for col in cursor.description]
            named = collections.namedtuple('Row', fields)
            return named(*row)

        db.row_factory = named_rows

        return cls(db)
    
    def append(self, address, metric, value, timestamp):
        parameters = (address, metric, value, timestamp)
        statement = '''
            INSERT INTO "log" (
                "id", "address",
                "metric", "value",
                "timestamp"
            ) VALUES (NULL, ?, ?, ?, ?)'''

        cursor = self.db.cursor()
        cursor.execute(statement, parameters)
        self.db.commit()

    def query(self, address=None, metric=None, after=None, before=None):
        parameters = (
            address, 0 if not address else 1,
            metric,  0 if not metric  else 1,
            after  or -sys.maxsize,
            before or +sys.maxsize)

        statement = '''
            SELECT "address", "metric", "value", "timestamp" FROM "log"
            WHERE (address=? OR 0=?) AND (metric=? OR 0=?)
            AND timestamp>=? AND timestamp<=?
            ORDER BY timestamp DESC'''

        cursor = self.db.cursor()
        return cursor.execute(statement, parameters)
