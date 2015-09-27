.. include:: ../../README.rst

Running as a Container
----------------------

.. image:: https://quay.io/repository/shad7/tvrenamer/status


The following will start a container using the default command `tvrename` using the configurations
provided by exposing a volume to the container to the mount point `/usr/etc/tvrenamer`.
The other volume mount points are used to provide direct access to a directory where
downloaded files exist and the base directory to your media library.

        docker pull shad7/tvrenamer
        or
        docker pull quay.io/shad7/tvrenamer

        docker run --rm \
        -v /path/to/downloads:/videos/downloads \
        -v /path/to/library:/videos/library \
        -v /path/to/configs/dir:/usr/etc/tvrenamer \
        shad7/tvrenamer


Contents:

.. toctree::
    :maxdepth: 1

    services
    results_processors
    options
    api/modules
    ChangeLog


.. only:: html

    Indices and tables
    ------------------

    * :ref:`genindex`
    * :ref:`search`

