import multiprocessing


class PoolSingleton:
    """
    A singleton class that manages a single instance of a multiprocessing pool.
    """
    _instance = None
    _pool = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def get_pool(self):
        if self._pool is None:
            self._pool = multiprocessing.Pool(processes=4)
        return self._pool

    def close_pool(self):
        if self._pool is not None:
            self._pool.close()
            self._pool.join()
            self._pool = None