from multiprocessing import Process


def _astrometry(location):
    import time
    time.sleep(10)


def solver(location=None):
    p = Process(target=_astrometry, args=(location,))
    p.start()
    p.join()
