import errno
import logging
import os

_LOG = logging.getLogger(__name__)


def mkdir_p(dirname):
    """Create a hierarchy of directories, if doesn't already exist see
    http://stackoverflow.com/a/600612/555656
    """
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(dirname):
            pass
        else:
            raise e
    else:
        _LOG.debug("Created directory {}".format(dirname))
