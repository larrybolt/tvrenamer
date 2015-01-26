"""Manages the execution of tasks using parallel processes."""
import logging
import time

import concurrent.futures as conc_futures
from oslo.config import cfg

from tvrenamer.common import tools
from tvrenamer.core import episode

LOG = logging.getLogger(__name__)

cfg.CONF.import_opt('max_processes', 'tvrenamer.options')


class Manager(object):
    """Manages a pool of processes and tasks.

    Executes the supplied tasks using the process pool.
    """

    def __init__(self):
        self.executor = conc_futures.ThreadPoolExecutor(
            cfg.CONF.max_processes)
        self.tasks = []

    def empty(self):
        """Checks if there are any tasks pending.

        :returns: True if no tasks else False
        :rtype: bool
        """
        return not self.tasks

    def add_tasks(self, tasks):
        """Adds tasks to list of tasks to be executed.

        :param tasks: a task or list of tasks to add to the list of
                      tasks to execute
        """
        if isinstance(tasks, list):
            self.tasks.extend(tasks)
        else:
            self.tasks.append(tasks)

    def run(self):
        """Executes the list of tasks.

        :return: the result/output from each tasks
        :rtype: list
        """
        futures_task = [self.executor.submit(task) for task in self.tasks]
        # always delete the tasks from task list to avoid duplicate execution
        # retrying of a task will be handled by the process that feeds us
        # the tasks.
        del self.tasks[:]

        results = {}
        for future in conc_futures.as_completed(futures_task):
            results.update(future.result())
        return results

    def shutdown(self):
        """Shuts down the process pool to free up resources."""
        self.executor.shutdown()


def _get_work(locations, processed):
    episodes = []
    for file in tools.retrieve_files(locations):
        if file not in processed:
            episodes.append(episode.Episode(file))
    return episodes


def start():
    """Entry point to start the processing.

    :returns: results from processing each file found
    :rtype: dict
    """

    mgr = Manager()
    locations = cfg.CONF.locations
    results = {}

    LOG.info('tvrenamer daemon starting up...')
    try:
        while True:
            # attempt to add tasks to the manager
            mgr.add_tasks(_get_work(locations, results))

            # if no work to do take a break and try again
            if mgr.empty():
                time.sleep(.5)
                continue

            # process the work
            results.update(mgr.run())

    except KeyboardInterrupt:
        # we were asked to stop from command line so simply stop
        pass
    finally:
        LOG.info('tvrenamer daemon shutting down...')
        mgr.shutdown()

    return results
