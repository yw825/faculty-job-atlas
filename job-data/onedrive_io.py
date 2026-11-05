"""Retry file opens that OneDrive refuses while it syncs the file.

OneDrive's file provider answers an open() of a file it is uploading with
OSError EDEADLK ("Resource deadlock avoided"). On 2026-11-02 that failed
114 schools' detail saves in one run and stopped the map rebuild, because
every stage reads and rewrites thousands of files in this synced folder.
The lock lasts seconds, so waiting and retrying is the whole fix.

Importing this module installs the retry into builtins.open, os.replace
and os.rename for the whole process; job_postings_lib imports it, so every
school script and pipeline stage gets it."""
import builtins
import errno
import os
import time

_RETRYABLE = {errno.EDEADLK, errno.EAGAIN, errno.EBUSY}
_ATTEMPTS = 20


def _with_retry(fn):
    if getattr(fn, '_onedrive_retry', False):
        return fn

    def wrapped(*args, **kwargs):
        delay = 0.5
        for attempt in range(_ATTEMPTS):
            try:
                return fn(*args, **kwargs)
            except OSError as e:
                if e.errno not in _RETRYABLE or attempt == _ATTEMPTS - 1:
                    raise
                time.sleep(delay)
                delay = min(delay * 1.5, 5)
    wrapped._onedrive_retry = True
    wrapped.__wrapped__ = fn
    return wrapped


builtins.open = _with_retry(builtins.open)
os.replace = _with_retry(os.replace)
os.rename = _with_retry(os.rename)
