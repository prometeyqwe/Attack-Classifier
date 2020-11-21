import signal
import subprocess

from time import time

from constants import SIGDESC


def sniffer_handler_run(pkg_out_queue, pkg_in_queue, logger):
    p = subprocess.Popen("/root/kdd99_feature_extractor/build-files/src/kdd99extractor", stdout=subprocess.PIPE, bufsize=1, shell=True, universal_newlines=True)
    sniffer = Sniffer(logger)

    for pkg in p.stdout:
        sniffer.pkg_handler(pkg)
        
        currentMinute = int(time() / 60)
        if sniffer.statMinute != currentMinute:
            sniffer.statMinute = currentMinute
            sniffer.get_stat_trace()

        if sniffer.pkg_amount % 10 or sniffer.statMinute != currentMinute:
            if sniffer.response_list:
                # sniffer.logger.info("from sniffer to main")
                pkg_out_queue.put_nowait(sniffer.response_list)
                sniffer.response_list = []

class Sniffer(object):
    def __init__(self, logger):
        self.pkg_amount = 0
        self.statMinute = int(time() / 60)
        self.response_list = []
        self.logger = logger
        signal.signal(signal.SIGTERM, self.signal_handler)
        self.logger.info("qwe2")

    def pkg_handler(self, pkg):
        self.pkg_amount += 1
        self.response_list.append(pkg)

    def signal_handler(self, sig_num, frame):
        self.logger.info("Sniffer::signal_handler() got signal {} {}, frame {}".format(
            sig_num, SIGDESC[sig_num], str(frame)
        ))

    def get_stat_trace(self):
        self.logger.info("SNIFFER::pkg_amount: {}".format(self.pkg_amount))