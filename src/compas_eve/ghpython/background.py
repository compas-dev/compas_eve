from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import threading
import time

import Rhino
import scriptcontext
import System
from compas_ghpython import create_id
from compas_ghpython import update_component


class BackgroundWorker(object):
    """Background worker simplifies the creation of long-running tasks inside Grasshopper.

    A long-running task is any piece of code that will run for an extended period of time,
    for example, a very complex calculation, or loading a very large data file, etc.

    To use it, start off from a simple Grasshopper GHPython component and retrieve an instance
    of the background worker with. The worker will stay working without blocking the UI.

    The following is an example of a GHPython component (in SDK mode) that launches a
    background task when it opens. The task is defined as the ``do_work`` function.

    .. code-block:: python

        import time
        from compas_eve.ghpython import BackgroundWorker

        from ghpythonlib.componentbase import executingcomponent as component


        def do_work(worker):
            # Call this function at the start of your long-running task to notify you have started
            worker.set_internal_state_to_working()
            worker.display_message("Starting task...")
            time.sleep(0.5)

            # Result can be of any data type
            result = 0

            for i in range(50):
                worker.current_value = i
                result += i
                worker.display_progress(i / (50-1))
                time.sleep(0.01)

            # Set the worker to do, and assigns the final results
            worker.set_internal_state_to_done(result)

        class ExampleComponent(component):
            def RunScript(self, start):
                self.worker = BackgroundWorker.instance_by_component(ghenv, do_work, force_new=start)

                if not self.worker.is_working() and not self.worker.is_done():
                    self.worker.start_work()

                print("Is worker working? {}".format(self.worker.is_working()))
                print("Is worker done? {}".format(self.worker.is_done()))

                if self.worker.is_done():
                    print("Completed")

                if hasattr(self.worker, "result"):
                    return (self.worker.result, )
                else:
                    return (None, )

    Parameters
    ----------
    ghenv : ``GhPython.Component.PythonEnvironment``
        Grasshopper environment object
    custom_work_callable : function, optional
        If defined, this function will be the main entry point for the long-running task.
    """

    def __init__(self, ghenv, custom_work_callable=None):
        super(BackgroundWorker, self).__init__()
        self.ghenv = ghenv
        self._is_working = False
        self._is_done = False
        self._is_cancelled = False
        self._has_requested_cancellation = False
        self.custom_work_callable = custom_work_callable

    def is_working(self):
        """Indicate whether the worker is currently working or not."""
        return self._is_working

    def is_done(self):
        """Indicate whether the worker is done or not."""
        return self._is_done

    def has_requested_cancellation(self):
        return self._has_requested_cancellation

    def request_cancellation(self):
        """Mark the current worker as cancelled, so that the background task can stop processing."""
        self._has_requested_cancellation = True

    def start_work(self):
        """Start the background processing thread where work will be performed."""
        if self.custom_work_callable:
            target = self.custom_work_callable
            args = (self,)
        else:
            target = self.do_work
            args = ()
        self.thread = threading.Thread(target=target, args=args)
        self.thread.start()

    def set_internal_state_to_working(self):
        """Set the internal state to ``working``."""
        self._is_working = True
        self._is_done = False
        self._is_cancelled = False

    def set_internal_state_to_done(self, result):
        """Set the internal state to ``done``, which indicates the worker has completed."""
        self._is_working = False
        self._is_done = True
        self._is_cancelled = False
        self.result = result
        update_component(self.ghenv, 1)

    def set_internal_state_to_cancelled(self):
        """Set the internal state to ``cancelled``."""
        self._is_working = False
        self._is_done = False
        self._is_cancelled = True

    def do_work(self):
        """Main entry point to define the work of a long-running task.

        This function should be overwritten in sub-classes of this one.

        The code of this function only an example of how to write a ``do_work`` method in a background worker.
        Within this function, the code can do whatever it needs: it can be blocking if needed, long/running, anything.

        The important bit is that it calls the methods ``set_internal_state_to_*`` at the right times
        to flag the status of the worker correctly.
        """
        self.set_internal_state_to_working()

        t = 200
        result = dict()
        for i in range(t):
            if self.has_requested_cancellation():
                self.display_message("Cancelled")
                self.set_internal_state_to_cancelled()
                break

            self.display_progress(i / (t - 1))
            time.sleep(1)

            result["a"] = "Counted up to {}".format(t)

        self.set_internal_state_to_done(result)

    def display_progress(self, progress):
        """Display a progress indicator in the component.

        Parameters
        ----------
        progress : float
            Float between ``0..1`` indicating progress of completion.
        """
        self.display_message("Progress {:.1f}%".format(progress * 100))

    def display_message(self, message):
        """Display a message in the component without triggering a solution expiration.

        Parameters
        ----------
        message : str
            Message to display.

        """

        def ui_callback():
            self.ghenv.Component.Message = message
            self.ghenv.Component.OnDisplayExpired(True)

        Rhino.RhinoApp.InvokeOnUiThread(System.Action(ui_callback))

    @classmethod
    def instance_by_component(cls, ghenv, custom_work_callable=None, force_new=False):
        """Get the worker instance assigned to the component.

        This will get a persistant instance of a background worker
        for a given component. The parameter `force_new` can
        be set to `True` to request a new instance to be created.

        Parameters
        ----------
        ghenv : ``GhPython.Component.PythonEnvironment``
            Grasshopper environment object
        custom_work_callable : function, optional
            If defined, this function will be the main entry point for the long-running task.
        force_new : bool, optional
            Force the creation of a new background worker, by default False.

        Returns
        -------
        :class:`BackgroundWorker`
            Instance of the background worker of the current component.
        """

        key = create_id(ghenv.Component, "background_worker")
        worker = scriptcontext.sticky.get(key)

        if worker and force_new:
            worker.request_cancellation()
            worker = None
            del scriptcontext.sticky[key]

        if not worker:
            if custom_work_callable:
                worker = cls(ghenv, custom_work_callable=custom_work_callable)
            else:
                worker = cls(ghenv)
            scriptcontext.sticky[key] = worker

        return worker
