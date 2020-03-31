from unittest.mock import patch
from django.test import TestCase
from django.core.management import call_command
from django.db.utils import OperationalError


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')

            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command("wait_for_db")

            self.assertEqual(gi.call_count, 6)

    def test_wait_for_db2(self):
        with patch('time.sleep') as ts:
            ts.return_value = True
            with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
                gi.side_effect = [OperationalError] * 5 + [True]
                call_command("wait_for_db")

                self.assertEqual(gi.call_count, 6)
