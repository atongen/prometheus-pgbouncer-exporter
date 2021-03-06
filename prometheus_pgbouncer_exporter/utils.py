# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import psycopg2


def get_connection(user=None, port=None, host=None, dbname='pgbouncer', password=None):
    kwargs = { 'user': user, 'port': port, 'host': host, 'dbname': dbname, 'password': password }
    kwargs = dict([(k, v) for k, v in kwargs.items() if v])
    connection = psycopg2.connect(
        **kwargs
    )

    # pgbouncer does not support transactions (as it does not make sense to),
    # so don't start a transaction when connecting
    connection.set_session(autocommit=True)

    return connection


def get_data_by_named_column(connection, key):
    with connection.cursor() as cursor:
        cursor.execute('SHOW %s;' % key)

        rows = cursor.fetchall()
        column_names = list(column.name for column in cursor.description)

    return [
        dict(zip(column_names, row))
        for row in rows
    ]


def get_data_by_named_row(connection, key):
    with connection.cursor() as cursor:
        cursor.execute('SHOW %s;' % key)

        return dict(cursor.fetchall())
