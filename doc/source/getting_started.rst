Getting Started
===============

Running locally / cron
----------------------

Create `virtualenv <http://www.virtualenv.org/en/latest/>`_ ::

    virtualenv ~/tvrenamer/

Start `virtualenv <http://www.virtualenv.org/en/latest/>`_ ::

    cd ~/tvrenamer
    source bin/activate

Install `tvrenamer <https://pypi.python.org/pypi/tvrenamer>`_ in the virtualenv::

    mkdir etc
    pip install tvrenamer

Running tvrenamer::

    tvrename

Running tvrenamer from crontab::

    crontab -e
    @hourly /home/USER/tvrenamer/bin/tvrename >> /home/USER/tvrenamer/etc/tvrenamer/cron.log 2>&1

.. note::

    As part of installing in virtualenv the sample configuration files will be installed into the
    **~/tvrenamer/etc/tvrenamer** folder.


Running as a Container
----------------------

.. image:: https://quay.io/repository/shad7/tvrenamer/status


The following will start a container using the default command `tvrename` using the configurations
provided by exposing a volume to the container to the mount point `/usr/etc/tvrenamer`.
The other volume mount points are used to provide direct access to a directory where
downloaded files exist and the base directory to your media library.

The pre-built images are published on `DockerHub <https://hub.docker.com/r/shad7/tvrenamer/>`_ and `Quay <https://quay.io/repository/shad7/tvrenamer>`_

.. code-block:: bash

        docker pull shad7/tvrenamer

        docker run --rm \
        -v /path/to/downloads:/videos/downloads \
        -v /path/to/library:/videos/library \
        -v /path/to/configs/dir:/usr/etc/tvrenamer \
        shad7/tvrenamer


.. code-block:: bash

        docker pull quay.io/shad7/tvrenamer

        docker run --rm \
        -v /path/to/downloads:/videos/downloads \
        -v /path/to/library:/videos/library \
        -v /path/to/configs/dir:/usr/etc/tvrenamer \
        quay.io/shad7/tvrenamer


**Congiguration**

Possible configuration file locations (General to specific)::

    /etc
    /etc/tvrenamer
    # if virtualenv used
    ~/tvrenamer/etc
    ~/tvrenamer/etc/tvrenamer
    ~
    ~/.tvrenamer
    <current working directory>

.. note::

    configuration filename: **tvrenamer.conf**

    virtualenv approach is the recommended approach. Multiple configuration files are supported such
    that each supported folder is checked for a configuration file and loaded from most general
    to more specific. Each successive file will override values from the previous.

    The folder of the most specific configuration file found will be considered the resource folder 
    where all log files are stored by default.

Command line interface::

        usage: tvrename [-h] [--cache_enabled] [--config-dir DIR] [--config-file PATH]
                        [--console_output_enabled] [--dryrun] [--logfile LOG_FILE]
                        [--loglevel LOG_LEVEL] [--nocache_enabled]
                        [--noconsole_output_enabled] [--nodryrun] [--version]
                        [locations [locations ...]]
        
        positional arguments:
          locations             specify the paths to search for files to rename.
        
        optional arguments:
          -h, --help            show this help message and exit
          --cache_enabled       Enable caching results
          --config-dir DIR      Path to a config directory to pull *.conf files from.
                                This file set is sorted, so as to provide a
                                predictable parse order if individual options are
                                over-ridden. The set is parsed after the file(s)
                                specified via previous --config-file, arguments hence
                                over-ridden options in the directory take precedence.
          --config-file PATH    Path to a config file to use. Multiple config files
                                can be specified, with values in later files taking
                                precedence. The default files used are: None.
          --console_output_enabled
                                Enable console output
          --dryrun              Practice run where no changes are applied.
          --logfile LOG_FILE    specify name of log file default: None
          --loglevel LOG_LEVEL  specify logging level to log messages: None
          --nocache_enabled     The inverse of --cache_enabled
          --noconsole_output_enabled
                                The inverse of --console_output_enabled
          --nodryrun            The inverse of --dryrun
          --version             show program's version number and exit


:doc:`options`
        A generated configuration file that contains each option a designation for required,
        a help message, default value, and associated type.


.. toctree::
    :hidden:

    options
