import json
import logging
from pyignite import Client

class ArenaJobRepository:
    """abstract base class."""
    def put(self, id, job):
        raise NotImplementedError()

    def get(self, id):
        raise NotImplementedError()

    def remove(self, id):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()


class ClientArenaJobRepository(ArenaJobRepository):
    LOG = logging.getLogger('ClientArenaJobRepository')

    def __init__(self, cluster_client):
        self.cluster_client = cluster_client
        self.jobs_cache = cluster_client.get_client().get_cache('arenajobs_json')
        self.jobs_cache_status = cluster_client.get_client().get_cache('arenajobs_status')

    def put(self, id, job_status):
        #self.jobs_cache.put(id, job)
        # just update status
        self.jobs_cache_status.put(id, job_status)

    def get(self, id):
        return self.jobs_cache.get(id)

    def get_as_json(self, id):
        job_json = self.get(id)
        if job_json is not None:
            return json.loads(job_json)
        return None

    def remove(self, id):
        self.jobs_cache.remove(id)

    def clear(self):
        if self.jobs_cache is not None:
            self.jobs_cache.clear()

    def get_jobs_cache(self):
        return self.jobs_cache

    def get_cluster_client(self):
        return self.cluster_client


class LassoClusterClient:
    def __init__(self, ssl_params, address='127.0.0.1:10800'):
        # Accept address as "host:port" or a list of such strings
        if isinstance(address, str):
            # If provided as a single address string
            host, port = address.split(':')
            self._addresses = [(host, int(port))]
        elif isinstance(address, (list, tuple)):
            # If provided as a list, convert each element
            self._addresses = []
            for addr in address:
                host, port = addr.split(':')
                self._addresses.append((host, int(port)))
        else:
            raise ValueError('address must be str or list/tuple of str')


        if ssl_params:
            self._client = Client(**ssl_params)
        else:
            self._client = Client()

        self._client.connect(self._addresses)

    def get_client(self):
        return self._client

    def close(self):
        self._client.close()