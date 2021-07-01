"""
Do again until stopped
"""
import traceback
import threading
from threading import Thread
import time


class DoAgain(Thread):

    def __init__(self, snapshots_interval=1, func=lambda counter: print(counter)):
        super().__init__()
        self._finished = threading.Event()
        self.snapshots_interval = snapshots_interval
        self.func = func

    def stop(self):
        self._finished.set()

    def run(self):
        last_call = time.time()
        counter = 0
        while not self._finished.is_set():
            if (time.time() - last_call) > self.snapshots_interval:
                last_call = time.time()
                try:
                    self.func(counter)
                    counter += 1
                except Exception:
                    print("Do Again Func failed")
                    print(traceback.format_exc())



def main():
    t = DoAgain(2)
    t.start()
    time.sleep(10)
    t.stop()
    t.join()


if __name__ == '__main__':
    print("start")
    main()
    print("done")
