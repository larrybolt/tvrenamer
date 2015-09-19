# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Justin Santa Barbara
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Generic Node base class for all workers that run on hosts."""

import abc
import contextlib
import errno
import io
import logging
import os
import signal
import socket
import sys
import threading

import eventlet
from eventlet import event
from eventlet import greenpool
import six


LOG = logging.getLogger(__name__)


def _sighup_supported():
    return hasattr(signal, 'SIGHUP')


def _is_daemon():
    # The process group for a foreground process will match the
    # process group of the controlling terminal. If those values do
    # not match, or ioctl() fails on the stdout file handle, we assume
    # the process is running in the background as a daemon.
    # http://www.gnu.org/software/bash/manual/bashref.html#Job-Control-Basics
    try:
        is_daemon = os.getpgrp() != os.tcgetpgrp(sys.stdout.fileno())
    except OSError as err:
        if err.errno == errno.ENOTTY:
            # Assume we are a daemon because there is no terminal.
            is_daemon = True
        else:
            raise
    except io.UnsupportedOperation:
        # Could not get the fileno for stdout, so we must be a daemon.
        is_daemon = True
    return is_daemon


def _is_sighup_and_daemon(signo):
    if not (_sighup_supported() and signo == signal.SIGHUP):
        # Avoid checking if we are a daemon, because the signal isn't
        # SIGHUP.
        return False
    return _is_daemon()


def _signo_to_signame(signo):
    signals = {signal.SIGTERM: 'SIGTERM',
               signal.SIGINT: 'SIGINT'}
    if _sighup_supported():
        signals[signal.SIGHUP] = 'SIGHUP'
    return signals[signo]


def _set_signals_handler(handler):
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)
    if _sighup_supported():
        signal.signal(signal.SIGHUP, handler)


def _abstractify(socket_name):
    if socket_name.startswith('@'):
        # abstract namespace socket
        socket_name = '\0%s' % socket_name[1:]
    return socket_name


def _sd_notify(unset_env, msg):
    notify_socket = os.getenv('NOTIFY_SOCKET')
    if notify_socket:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        with contextlib.closing(sock):
            try:
                sock.connect(_abstractify(notify_socket))
                sock.sendall(msg)
                if unset_env:
                    del os.environ['NOTIFY_SOCKET']
            except EnvironmentError:
                LOG.debug("Systemd notification failed", exc_info=True)


def notify_once():
    """Send notification once to Systemd that service is ready.

    Systemd sets NOTIFY_SOCKET environment variable with the name of the
    socket listening for notifications from services.
    This method removes the NOTIFY_SOCKET environment variable to ensure
    notification is sent only once.
    """
    _sd_notify(True, 'READY=1')


def _thread_done(gt, *args, **kwargs):
    """Callback function to be passed to GreenThread.link() when we spawn()

    Calls the :class:`ThreadGroup` to notify if.
    """
    kwargs['group'].thread_done(kwargs['thread'])


class Thread(object):
    """Wrapper around a greenthread.

    Holds a reference to the :class:`ThreadGroup`. The Thread will notify
    the :class:`ThreadGroup` when it has done so it can be removed from the
    threads list.
    """
    def __init__(self, thread, group):
        self.thread = thread
        self.thread.link(_thread_done, group=group, thread=self)

    def stop(self):
        self.thread.kill()

    def wait(self):
        return self.thread.wait()

    def link(self, func, *args, **kwargs):
        self.thread.link(func, *args, **kwargs)


class ThreadGroup(object):
    """The point of the ThreadGroup class is to:

    * greenthreads (making it easier to stop them when need be).
    """
    def __init__(self, thread_pool_size=10):
        self.pool = greenpool.GreenPool(thread_pool_size)
        self.threads = []

    def add_thread(self, callback, *args, **kwargs):
        gt = self.pool.spawn(callback, *args, **kwargs)
        th = Thread(gt, self)
        self.threads.append(th)
        return th

    def thread_done(self, thread):
        self.threads.remove(thread)

    def _stop_threads(self):
        current = threading.current_thread()

        # Iterate over a copy of self.threads so thread_done doesn't
        # modify the list while we're iterating
        for x in self.threads[:]:
            if x is current:
                # don't kill the current thread.
                continue
            try:
                x.stop()
            except eventlet.greenlet.GreenletExit:
                pass
            except Exception:
                LOG.exception('Error stopping thread.')

    def stop(self, graceful=False):
        """stop function has the option of graceful=True/False.

        * In case of graceful=True, wait for all threads to be finished.
          Never kill threads.
        * In case of graceful=False, kill threads immediately.
        """
        if graceful:
            # In case of graceful=True, wait for all threads to be
            # finished, never kill threads
            self.wait()
        else:
            # In case of graceful=False(Default), kill threads
            # immediately
            self._stop_threads()

    def wait(self):
        current = threading.current_thread()

        # Iterate over a copy of self.threads so thread_done doesn't
        # modify the list while we're iterating
        for x in self.threads[:]:
            if x is current:
                continue
            try:
                x.wait()
            except eventlet.greenlet.GreenletExit:
                pass
            except Exception:
                LOG.exception('Error waiting on ThreadGroup.')


def _check_service_base(service):
    if not isinstance(service, ServiceBase):
        raise TypeError('Service %(service)s must an instance of %(base)s!'
                        % {'service': service, 'base': ServiceBase})


@six.add_metaclass(abc.ABCMeta)
class ServiceBase(object):
    """Base class for all services."""

    @abc.abstractmethod
    def start(self):
        """Start service."""

    @abc.abstractmethod
    def stop(self):
        """Stop service."""

    @abc.abstractmethod
    def wait(self):
        """Wait for service to complete."""

    @abc.abstractmethod
    def reset(self):
        """Reset service.

        Called in case service running in daemon mode receives SIGHUP.
        """


class Launcher(object):
    """Launch one or more services and wait for them to complete."""

    def __init__(self, conf):
        """Initialize the service launcher.

        :returns: None

        """
        self.conf = conf
        self.services = Services()

    def launch_service(self, service):
        """Load and start the given service.

        :param service: The service you would like to start.
        :returns: None

        """
        _check_service_base(service)
        self.services.add(service)

    def stop(self):
        """Stop all services which are currently running.

        :returns: None

        """
        self.services.stop()

    def wait(self):
        """Waits until all services have been stopped, and then returns.

        :returns: None

        """
        self.services.wait()

    def restart(self):
        """Reload config files and restart service.

        :returns: None

        """
        self.conf.reload_config_files()
        self.services.restart()


class SignalExit(SystemExit):
    def __init__(self, signo, exccode=1):
        super(SignalExit, self).__init__(exccode)
        self.signo = signo


class ServiceLauncher(Launcher):
    """Runs one or more service in a parent process."""
    def __init__(self, conf):
        """Constructor.

        :param conf: an instance of ConfigOpts
        """
        super(ServiceLauncher, self).__init__(conf)

    def _handle_signal(self, signo, frame):
        # Allow the process to be killed again and die from natural causes
        _set_signals_handler(signal.SIG_DFL)
        raise SignalExit(signo)

    def handle_signal(self):
        _set_signals_handler(self._handle_signal)

    def _wait_for_exit_or_signal(self, ready_callback=None):
        status = None
        signo = 0

        try:
            if ready_callback:
                ready_callback()
            super(ServiceLauncher, self).wait()
        except SignalExit as exc:
            signame = _signo_to_signame(exc.signo)
            LOG.info('Caught %s, exiting', signame)
            status = exc.code
            signo = exc.signo
        except SystemExit as exc:
            status = exc.code
        finally:
            self.stop()

        return status, signo

    def wait(self, ready_callback=None):
        notify_once()
        _set_signals_handler(signal.SIG_DFL)
        while True:
            self.handle_signal()
            status, signo = self._wait_for_exit_or_signal(ready_callback)
            if not _is_sighup_and_daemon(signo):
                return status
            self.restart()


class Service(ServiceBase):
    """Service object for binaries running on hosts."""

    def __init__(self, threads=1000):
        self.tg = ThreadGroup(threads)

        # signal that the service is done shutting itself down:
        self._done = event.Event()

    def reset(self):
        # NOTE(Fengqian): docs for Event.reset() recommend against using it
        self._done = event.Event()

    def start(self):
        """Start a service."""

    def stop(self, graceful=False):
        self.tg.stop(graceful)
        self.tg.wait()
        # Signal that service cleanup is done:
        if not self._done.ready():
            self._done.send()

    def wait(self):
        self._done.wait()


class Services(object):

    def __init__(self):
        self.services = []
        self.tg = ThreadGroup()
        self.done = event.Event()

    def add(self, service):
        self.services.append(service)
        self.tg.add_thread(self.run_service, service, self.done)

    def stop(self):
        # wait for graceful shutdown of services:
        for service in self.services:
            service.stop()

        # Each service has performed cleanup, now signal that the run_service
        # wrapper threads can now die:
        if not self.done.ready():
            self.done.send()

        # reap threads:
        self.tg.stop()

    def wait(self):
        for service in self.services:
            service.wait()
        self.tg.wait()

    def restart(self):
        self.stop()
        self.done = event.Event()
        for restart_service in self.services:
            restart_service.reset()
            self.tg.add_thread(self.run_service, restart_service, self.done)

    @staticmethod
    def run_service(service, done):
        """Service start wrapper.

        :param service: service to run
        :param done: event to wait on until a shutdown is triggered
        :returns: None

        """
        service.start()
        done.wait()


def launch(conf, service):
    launcher = ServiceLauncher(conf)
    launcher.launch_service(service)
    return launcher
