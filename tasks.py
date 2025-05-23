from typing import Callable
from threading import Thread, Event


class ProgramKilled(Exception):
    pass


def sig_handler(signum, frame):
    raise ProgramKilled


class BaseTask(Thread):
    def __init__(self, interval, execute, *args):
        Thread.__init__(self)

        self.daemon: bool = False
        self.stopped: Event = Event()
        self.interval: int = interval
        self.execute: Callable = execute
        self.args = args


class ParsingTask(BaseTask):

    def stop(self):
        self.stopped.set()
        self.join()

    def run(self):
        while not self.stopped.wait(self.interval):
            self.execute(*self.args)


def parsing_task(parser):
    parser.login()
    parser.load_winners()
