"""Manages the execution of tasks using parallel processes."""
import logging
import time

import concurrent.futures as conc_futures
from oslo_config import cfg
import six

from tvrenamer import cache
from tvrenamer.common import tools
from tvrenamer.core import episode

LOG = logging.getLogger(__name__)

cfg.CONF.import_opt('max_processes', 'tvrenamer.options')
cfg.CONF.import_opt('enabled', 'tvrenamer.cache', 'database')


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

        results = []
        for future in conc_futures.as_completed(futures_task):
            results.append(future.result())
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


def _handle_results(results):

    if cfg.CONF.database.enabled:
        for res in results:
            cache.dbapi().save(cache.MediaFile(
                original=res.original,
                name=res.name,
                extension=res.extension,
                location=res.location,
                clean_name=res.clean_name,
                series_name=res.series_name,
                season_number=res.season_number,
                episode_numbers=','.join(
                    str(e) for e in res.episode_numbers or []),
                episode_names=','.join(res.episode_names or []),
                formatted_filename=res.formatted_filename,
                formatted_dirname=res.formatted_dirname,
                state=res.state,
                messages='\n'.join(res.messages)
                ))

    output = {}
    for r in results:
        output.update(r.status)

    # if logging is not enabled then no need to
    # go any further.
    if LOG.isEnabledFor(logging.INFO):

        for epname, result in six.iteritems(output):
            status = 'SUCCESS' if result.get('result') else 'FAILURE'
            LOG.info('[%s]: %s --> %s', status, epname,
                     result.get('formatted_filename'))
            LOG.info('\tPROGRESS: %s', result.get('progress'))
            if result.get('messages'):
                LOG.info('\tREASON: %s', result.get('messages'))

    return output


def start():
    """Entry point to start the processing.

    :returns: results from processing each file found
    :rtype: dict
    """

    mgr = Manager()
    locations = cfg.CONF.locations or []
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
            results.update(_handle_results(mgr.run()))

    except KeyboardInterrupt:
        # we were asked to stop from command line so simply stop
        pass
    finally:
        LOG.info('tvrenamer daemon shutting down...')
        mgr.shutdown()
