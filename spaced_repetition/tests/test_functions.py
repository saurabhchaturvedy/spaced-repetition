#!/usr/bin/env python3
"""Tests for utility functions."""
import contextlib
import datetime
import sys
import unittest
from io import StringIO
from urllib import parse

from spaced_repetition.env import *
from spaced_repetition.functions import *
from spaced_repetition import database

class TestFunctions(unittest.TestCase):
    """Tests for utility functions."""
    url = parse.urlparse(TEST_DATABASE_URL)
    conn = database.db_connect(url)
    dsn = database.get_dsn(conn)
    cur = conn.cursor()

    def test_get_next_date(self):
        day = datetime.datetime.strptime('19081998', '%d%m%Y').date()
        next_day = datetime.datetime.strptime('20081998', '%d%m%Y').date()
        self.assertEqual(get_next_date(day, 1), next_day)

        today = datetime.datetime.now().date()
        tomorrow = today + datetime.timedelta(days=1)
        self.assertEqual(get_next_date(today, 1), tomorrow)

    def test_learn_today(self):
        self.assertEqual(type(learn_today(self.cur)), list)

    def test_get_colnames(self):
        self.cur.execute("SELECT id, title, add_date from to_learn")
        self.assertEqual(get_colnames(self.cur), ['id', 'title', 'add_date'])

    def test_display_rows(self):
        # Make this drier.
        out = StringIO()
        self.cur.execute(
            "SELECT id, title, add_date from to_learn WHERE id=0"
            )
        with contextlib.redirect_stdout(out):
            display_rows(self.cur)
        output = out.getvalue()
        expected = "id title                     add_date   \n\n"\
                   "0  Polynomial Multiplication 2017-12-19 \n"
        self.assertEqual(output, expected)

        out = StringIO()
        self.cur.execute(
            "SELECT id, title, add_date from to_learn WHERE id=1"
            )
        with contextlib.redirect_stdout(out):
            display_rows(self.cur)
        output = out.getvalue()
        expected = "id title                       add_date   \n\n"\
                   "1  Design of Computer Programs 2017-10-20 \n"
        self.assertEqual(output, expected)

    def test_display_todays_stuff(self):
        out = StringIO()
        with contextlib.redirect_stdout(out):
            display_todays_stuff(self.cur)
        output = out.getvalue()
        self.assertTrue(len(output) > 0)
    
    def test_insert_source(self):
        title, begin_date_str = "The Book", "05-01-2018"
        test_input = "%s\n%s\n" % (title, begin_date_str)
        inp = StringIO(test_input)
        sys.stdin = inp
        insert_source(self.cur)
        sys.stdin = sys.__stdin__  # Reset to the 'real' standand input.
        self.cur.execute(
            "SELECT title, begin_date, total_entries FROM notebooks "
            "WHERE title = 'The Book'"
        )
        row = self.cur.fetchone()
        self.cur.execute("DELETE FROM notebooks WHERE title='The Book'")
        self.cur.connection.commit()
        begin_date = datetime.datetime.strptime(begin_date_str, "%d-%m-%Y").date()
        self.assertEqual(row, (title, begin_date, 0))

    def test_insert_entry(self):
        title = "Quantum Tunneling"
        page_num_start, page_num_end = 3, 6
        add_date = "05-01-2018"
        last_revision = "05-01-2018"
        input_tuple = (title, page_num_start, page_num_end, add_date,
                       last_revision)
        test_input = "%s\n%s\n%s\n%s\n%s\n\n" % input_tuple
        inp = StringIO(test_input)
        sys.stdin = inp
        insert_entry(self.cur)
        sys.stdin = sys.__stdin__
        self.cur.execute("SELECT title, page_num_start, page_num_end, "
                         "add_date, last_revision, level "
                         "FROM to_learn WHERE title='Quantum Tunneling'")
        values_tuple = (title, page_num_start, page_num_end,
                        datetime.datetime.strptime(add_date, '%d-%m-%Y').date(),
                        datetime.datetime.strptime(last_revision, '%d-%m-%Y').date(),
                        1)
        row = self.cur.fetchone()
        self.assertEqual(row, values_tuple)


if __name__ == '__main__':
    unittest.main()
