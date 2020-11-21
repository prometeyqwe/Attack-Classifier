import logging
import signal
from time import time
from multiprocessing import Process, Queue
from logging.handlers import WatchedFileHandler

from constants import SIGDESC
from worker import worker_handler_run
from sniffer import Sniffer, sniffer_handler_run


is_stopped = False
def signal_handler(sig_num, frame):
      global is_stopped
      print("Main::signal_handler() got signal {} {}, frame {}".format(
            sig_num, SIGDESC[sig_num], str(frame)
        ))
      
      is_stopped = True

if __name__ == '__main__':
      defaults = {
            'filename': '/var/log/diplom/diplom.log',
            'format': '%(asctime)s.%(msecs)06d [%(process)d] %(levelname)-7s ---> %(name)s::%(funcName)s() %(message)s',
            'level': logging.DEBUG,
            'datefmt': '%Y-%m-%d %H:%M:%S',
      }

      formatter = logging.Formatter(defaults['format'], defaults['datefmt'])
      handler = WatchedFileHandler(defaults['filename'])
      handler.setFormatter(formatter)
      logging.basicConfig(**defaults)
      logger = logging.getLogger('Core')
      logger.setLevel(logging.DEBUG)
      logger.info("qwe0")
      from_sniffer_pkg_list = []
      signal.signal(signal.SIGTERM, signal_handler)

      sniffer_traffic_in_queue = Queue(maxsize=100000)
      sniffer_traffic_out_queue = Queue(maxsize=10000)
      sniffer_process = Process(target=sniffer_handler_run, args=[sniffer_traffic_in_queue, sniffer_traffic_out_queue, logger])
      sniffer_process.start()

      worker_traffic_in_queue = Queue(maxsize=100000)
      worker_traffic_out_queue = Queue(maxsize=100000)
      worker_process = Process(target=worker_handler_run, args=[worker_traffic_in_queue, worker_traffic_out_queue, logger])
      worker_process.start()
      
      while not is_stopped:
            if not sniffer_traffic_in_queue.empty():
                  pkg_list = sniffer_traffic_in_queue.get_nowait()
                  from_sniffer_pkg_list.extend(pkg_list)

            if from_sniffer_pkg_list:
                  # logger.info("from sniffer")
                  worker_traffic_out_queue.put_nowait(from_sniffer_pkg_list)
                  from_sniffer_pkg_list = []
            
            if not worker_traffic_in_queue.empty():
                  # logger.info("from worker to main")
                  pkg_list  = worker_traffic_in_queue.get_nowait()
                  for pkg in pkg_list:
                        # logger.info(pkg)
                        pass

      logger.info("Stop MAIN module.")
      worker_process.join()
      sniffer_process.join()