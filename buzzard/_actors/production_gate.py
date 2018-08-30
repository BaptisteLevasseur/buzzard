from buzzard._actors.message import Msg

class ActorProductionGate(object):
    """Actor that takes care of """

    def __init__(self, raster):
        self._raster = raster
        self._queries = {}
        self._alive = True

    @property
    def address(self):
        return '/Raster{}/ProductionGate'.format(self._raster.uid)

    @property
    def alive(self):
        return self._alive

    # ******************************************************************************************* **
    def receive_make_those_arrays(self, qi):
        msgs = []
        assert qi not in self._queries

        q = _Query()
        self._queries[qi] = q
        msgs += self._allow(qi, q, 0)
        return msgs

    def receive_output_queue_update(self, qi, produced_count, queue_size):
        msgs = []

        assert qi in self._queries
        q = self._queries[qi]

        if produced_count == qi.produce_count:
            assert qi.allowed_count == produce_count
        else:
            pulled_count = produce_count - queue_size
            msgs += self._allow(qi, q, pulled_count)

        return msgs

    def receive_cancel_this_query(self, qi):
        """Receive message: One query was dropped

        Parameters
        ----------
        qi: _actors.cached.query_infos.QueryInfos
        """
        del self._queries[qi]
        return []

    def receive_die(self):
        """Receive message: The raster was killed"""
        assert self._alive
        self._alive = False

        self._queries.clear()
        return []

    # ******************************************************************************************* **
    @staticmethod
    def _allow(qi, q, pulled_count):
        msgs = []

        # One of the two mighty condition that prevents backpressure between rasters
        while q.allowed_count < qi.produce_count and q.allowed_count - qi.max_queue_size < pulled_count:
            msgs += [Msg(
                'Producer', 'make_this_array', q.allowed_count
            )]
            q.allowed_count += 1

        return msgs


    # ******************************************************************************************* **

class _Query(object):

    def __init__(self):
        self.allowed_count = 0
