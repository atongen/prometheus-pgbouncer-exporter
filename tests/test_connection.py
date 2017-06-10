import unittest

from unittest.mock import patch, Mock

from prometheus_pgbouncer_exporter import utils

class ConnectionTest(unittest.TestCase):
    @patch('prometheus_pgbouncer_exporter.utils.psycopg2.connect')
    def test_get_connection_with_password_works(self, connect):
        conn = utils.get_connection(host='/tmp/', dbname='template1')
        connect.assert_called_once_with(host='/tmp/', dbname='template1')
        connect.return_value.set_session.assert_called_once_with(autocommit=True)
