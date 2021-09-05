import os
from flask import g
import psycopg2
from psycopg2.extras import RealDictCursor

# make Decimal types float to be json serializable
DEC2FLOAT = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMAL.values,
    "DEC2FLOAT",
    lambda value, curs: float(value) if value is not None else None,
)
psycopg2.extensions.register_type(DEC2FLOAT)

# make DateTime types to be json serializable
DATETIME2JSON = psycopg2.extensions.new_type(
    psycopg2.extensions.PYDATETIMETZ.values,
    "DATETIME2JSON",
    lambda value, curs: value.replace(" ", "T") if value is not None else None,
)
psycopg2.extensions.register_type(DATETIME2JSON)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        # connect: "user='blahdb' password='blahblah' host='blah.com' dbname='blahdb'"
        # RealDictCursor necessary to return dicts instead of arrays from db
        conn = psycopg2.connect(
            os.getenv("DB_CONN_STRING"), cursor_factory=RealDictCursor
        )
        conn.set_session(autocommit=True)
        db = g._database = conn
    return db
