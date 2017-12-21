#!/usr/bin/env python3
"""Database interface functions to be used elsewhere."""
import datetime
import psycopg2

def db_connect(url):
    """Returns a database connection object."""
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    return conn


def get_dsn(conn):
    """Gets few connection attributes."""
    attributes_list = conn.dsn.split()
    attributes = {}
    for attribute_str in attributes_list:
        pair = attribute_str.split('=')
        key, value = pair[0], pair[1]
        attributes[key] = value
    return attributes


def get_last_rev_with_id_and_level(cur):
    """Gets last revisions for all items with their ids."""
    cur.execute("SELECT id, last_revision, level from to_learn")
    return cur


def get_rows_for_ids(cur, ids):
    """Fetches rows with given ids."""
    # Following line is hacky. Fix it ASAP!
    cur.execute("SELECT * FROM to_learn WHERE id IN %s", (tuple(ids),))
    return cur


def set_for_next_date(cur, ids):
    """Update level and prev_date after revision is done."""
    # Fix the following hacky query ASAP.
    cur.execute("UPDATE to_learn SET last_revision=%s, level=level+1 WHERE id IN %s",
                (datetime.datetime.now().date(), tuple(ids))
               )
    cur.connection.commit()