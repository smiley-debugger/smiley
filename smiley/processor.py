"""Base class for event processors so the APIs are consistent.
"""
import abc


class EventProcessor(object):
    """Base class for things that work with the events from the tracer.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def start_run(self, run_id, cwd, description, start_time):
        """Called when a 'start_run' event is seen.
        """

    @abc.abstractmethod
    def end_run(self, run_id, end_time, message, traceback, stats):
        """Called when an 'end_run' event is seen.
        """

    @abc.abstractmethod
    def trace(self, run_id, event,
              func_name, line_no, filename,
              trace_arg, local_vars,
              timestamp):
        """Called when any other event type is seen.
        """
