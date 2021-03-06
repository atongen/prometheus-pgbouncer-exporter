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

from prometheus_client.core import GaugeMetricFamily

from .utils import get_data_by_named_column, get_data_by_named_row


class PgBouncerCollector(object):
    def __init__(self, connection, namespace='pgbouncer'):
        self.connection = connection
        self.namespace = namespace


class NamedColumnCollector(PgBouncerCollector):
    def get_labels_for_row(self, row):
        raise NotImplementedError()

    def collect(self):
        # Each of the metrics is recorded per database, by calling add_metric
        # with the database as the label on the appropriate GaugeMetricFamily.

        # First, create the GaugeMetricFamily objects for each metric
        gauges = {
            key: GaugeMetricFamily(
                name="%s_%s" % (self.namespace, name),
                documentation="%s (%s)" % (documentation, key),
                labels=self.labels,
            )
            for key, (name, documentation) in self.metrics.items()
        }

        rows = get_data_by_named_column(self.connection, self.query_parameter)

        # Each row coresponds to the metrics for a particular database
        for row in rows:
            database = row['database']

            if self.databases is not None and database not in self.databases:
                continue

            # Sort for deterministic ordering in the output
            for key in sorted(self.metrics.keys()):
                value = row.get(key, None)
                if value is not None:
                    label_values = self.get_labels_for_row(row)

                    gauges[key].add_metric(label_values, value)

        for gauge in gauges.values():
            yield gauge


class ListsCollector(PgBouncerCollector):
    metrics = {
        'databases': (
            'databases',
            "Number of databases",
        ),
        'users': (
            'users',
            "Number of users",
        ),
        'pools': (
            'pools',
            "Number of pools",
        ),
        'free_clients': (
            'free_clients',
            "Number of free clients",
        ),
        'used_clients': (
            'used_clients',
            "Number of used clients",
        ),
        'login_clients': (
            'login_clients',
            "Number of clients in the login stats",
        ),
        'free_servers': (
            'free_servers',
            "Number of free servers",
        ),
        'used_servers': (
            'used_servers',
            "Number of used servers",
        ),
        'dns_names': (
            'dns_names',
            "",
        ),
        'dns_zones': (
            'dns_zones',
            "",
        ),
        'dns_queries': (
            'dns_queries',
            "",
        ),
        'dns_pending': (
            'dns_pending',
            "",
        ),
    }

    def collect(self):
        data = get_data_by_named_row(self.connection, 'LISTS')

        for key, (name, documentation) in sorted(
            self.metrics.items(), key=lambda x: x[0]
        ):
            yield GaugeMetricFamily(
                name="%s_%s" % (self.namespace, name),
                documentation="%s (%s)" % (documentation, key),
                value=data[key],
            )


class StatsCollector(NamedColumnCollector):
    query_parameter = 'STATS'

    labels = ['database']

    metrics = {
        'total_xact_count': (
            'xacts_total',
            "Total number of transactions pooled by pgbouncer"
        ),
        'total_query_count': (
            'queries_total',
            "Total number of queries pooled by pgbouncer"
        ),
        'total_xact_time': (
            'xact_microseconds_total',
            "Total number of microseconds spent in transaction by pgbouncer",
        ),
        'total_wait_time': (
            'wait_microseconds_total',
            "Total number of microseconds spent waiting by pgbouncer",
        ),
        'total_requests': (
            'requests_total',
            "Total number of SQL requests pooled by pgbouncer",
        ),
        'total_received': (
            'received_bytes_total',
            "Total volume in bytes of network traffic received by pgbouncer",
        ),
        'total_sent': (
            'sent_bytes_total',
            "Total volume in bytes of network traffic sent by pgbouncer",
        ),
        'total_query_time': (
            'query_microseconds_total',
            "Total number of microseconds spent by pgbouncer when actively connected to PostgreSQL",
        ),
    }

    def __init__(self, databases, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.databases = databases

    def get_labels_for_row(self, row):
        return [row['database']]


class PoolsCollector(NamedColumnCollector):
    query_parameter = 'POOLS'

    labels = ['database', 'user']

    metrics = {
        'cl_active': (
            'active_clients',
            "Client connections that are linked to server connection and can process queries",
        ),
        'cl_waiting': (
            'waiting_clients',
            "Client connections have sent queries but have not yet got a server connection",
        ),
        'sv_active': (
            'sv_active',
            "Server connections that linked to client.",
        ),
        'sv_idle': (
            'sv_idle',
            "Server connections that unused and immediately usable for client queries.",
        ),
        'sv_used': (
            'sv_used',
            "Server connections that have been idle more than server_check_delay, so they needs server_check_query to run on it before it can be used.",
        ),
        'sv_tested': (
            'sv_tested',
            "Server connections that are currently running either server_reset_query or server_check_query.",
        ),
        'sv_login': (
            'sv_login',
            "Server connections currently in logging in process.",
        ),
    }

    def __init__(self, databases, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.databases = databases

    def get_labels_for_row(self, row):
        return [row['database'], row['user']]


class DatabasesCollector(NamedColumnCollector):
    query_parameter = 'DATABASES'

    labels = ['database']

    metrics = {
        'pool_size': (
            'pool_size',
            "",
        ),
        'reserve_pool': (
            'reserve_pool',
            "",
        ),
    }

    def __init__(self, databases, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.databases = databases

    def get_labels_for_row(self, row):
        return [row['database']]
