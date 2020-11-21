import torch
import signal

from time import time
from collections import deque

from constants import SIGDESC
from net import NeuralNetwork


# model = NeuralNetwork(20, 7, 23)
# model.load_state_dict(torch.load("/Users/prometey_qwe/Documents/diplom/program/net"))
# model.eval()


# x = [  0.,   0.,  14.,   9.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
#         0.,   0.,   0.,   0.,   0.,   0., 255.,   0.]

# y = 18

# y_pred = model(torch.tensor([x]))
# y_pred = y_pred.argmax(dim=1)


# print(y_pred)

class Worker(object):
    def __init__(self, logger):
        self.request_list = deque()
        self.response_list = []
        signal.signal(signal.SIGTERM, self.signal_handler)
        self.logger = logger
        self.logger.info("qwe1")
        self.statMinute = int(time() / 60)
        self.pkg_amount = 0

    def signal_handler(self, sig_num, frame):
        self.logger.info("Worker::signal_handler() got signal {} {}, frame {}".format(
            sig_num, SIGDESC[sig_num], str(frame)
        ))

    def get_stat_trace(self):
        self.logger.info("WORKER::pkg_amount: {}".format(self.pkg_amount))
    
    def package_handler(self, pkg):
        self.pkg_amount += 1
        """ return result pkg """

        return None

    def handler(self):
        while self.request_list:
            pkg = self.request_list.popleft()
            self.response_list.append(self.package_handler(pkg))

def worker_handler_run(pkg_out_queue, pkg_in_queue, logger):
    worker = Worker(logger)

    while True:
        worker.handler()

        if not pkg_in_queue.empty():
            pkg_list = pkg_in_queue.get_nowait()
            worker.request_list.extend(pkg_list)

        if worker.response_list:
            pkg_out_queue.put_nowait(worker.response_list)
            worker.response_list = []

        currentMinute = int(time() / 60)
        if worker.statMinute != currentMinute:
            worker.statMinute = currentMinute
            worker.get_stat_trace()