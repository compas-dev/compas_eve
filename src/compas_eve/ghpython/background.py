import threading
from typing import Any
from typing import Callable
from typing import Optional

try:
    import Rhino
    import scriptcontext
    import System
    from compas_ghpython import create_id
    from compas_ghpython.timer import update_component
except ImportError:
    pass


class BackgroundWorker(object):
    """Background worker simplifies the creation of long-running tasks inside Grasshopper.

    A long-running task is any piece of code that will run for an extended period of time,
    for example, a very complex calculation, or loading a very large data file, etc.

    To use it, write your long-running function in a Grasshopper GHPython component,
    and pass it as the input to the background worker component.
    The worker will continue working without blocking the UI.

    The following is an example of a long-running function that updates the
    progress while it runs.

    ```python
    import time


    def do_something_long_and_complicated(worker):
        # Result can be of any data type
        result = 0

        for i in range(50):
            worker.current_value = i
            result += i
            worker.display_progress(i / (50 - 1))
            time.sleep(0.01)

        worker.display_message("Done!")

        return result
    ```

    Parameters
    ----------
    ghenv
        Grasshopper environment object
    long_running_function
        This function will be the main entry point for the long-running task.
    dispose_function
        If defined, this function will be called when the worker is disposed. It can be used for clean-up tasks
        and resource deallocation.
    auto_set_done
        If true, the worker state will be automatically set to `Done` after the function returns.
        Defaults to `True`.
    args
        List or tuple of arguments for the invocation of the `long_running_function`. Defaults to `()`.
    """

    def __init__(
        self,
        ghenv: "GhPython.Component.PythonEnvironment",
        long_running_function: Optional[Callable] = None,
        dispose_function: Optional[Callable] = None,
        auto_set_done: bool = True,
        args=(),
    ):
        super(BackgroundWorker, self).__init__()
        self.ghenv = ghenv
        self._is_working = False
        self._is_done = False
        self._is_cancelled = False
        self._has_requested_cancellation = False
        self.long_running_function = long_running_function
        self.dispose_function = dispose_function
        self.auto_set_done = auto_set_done
        self.args = args

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

        def _long_running_task_wrapper(worker):
            try:
                worker.set_internal_state_to_working()
                result = self.long_running_function(self, *self.args)

                # There are (at least) two types of long running functions:
                # 1. Those that block the thread while working
                #    (e.g. they have a busy-wait or some kind of `while` loop)
                # 2. Those that hookup event handlers and return immediately
                #    so then they don't need to block the thread.
                # The first case means that we can set the state to "DONE"
                # right after calling the function because if it returned, it really
                # means it's done.
                # The second case will return immediately, and setting the state to "DONE"
                # would be wrong because the handlers are still going to trigger.
                # In that case we can set the flag `auto_set_done` to `False` so that
                # we don't automatically set the state to "DONE".
                if self.auto_set_done:
                    worker.set_internal_state_to_done(result)
            except Exception as e:
                worker.display_message(str(e))
                worker.set_internal_state_to_cancelled()

        target = _long_running_task_wrapper
        args = (self,)
        self.thread = threading.Thread(target=target, args=args)
        self.thread.daemon = True
        self.thread.start()

    def dispose(self):
        """Invoked when the worker is being disposed."""
        if callable(self.dispose_function):
            self.dispose_function(self)

    def set_internal_state_to_working(self):
        """Set the internal state to `working`."""
        self._is_working = True
        self._is_done = False
        self._is_cancelled = False

    def set_internal_state_to_done(self, result: Any):
        """Set the internal state to `done`, which indicates the worker has completed."""
        self._is_working = False
        self._is_done = True
        self._is_cancelled = False
        self.update_result(result, delay=1)

    def update_result(self, result: Any, delay: int = 1):
        """Update the result of the worker.

        This will update the result of the worker, and trigger a solution expiration
        of the Grasshopper component.

        Parameters
        ----------
        result
            Result of the worker.
        delay
            Delay (in milliseconds) before updating the component, by default 1.
        """
        self.result = result
        update_component(self.ghenv, delay)

    def set_internal_state_to_cancelled(self):
        """Set the internal state to `cancelled`."""
        self._is_working = False
        self._is_done = False
        self._is_cancelled = True

    def display_progress(self, progress: float):
        """Display a progress indicator in the component.

        Parameters
        ----------
        progress
            Float between `0..1` indicating progress of completion.
        """
        self.display_message("Progress {:.1f}%".format(progress * 100))

    def display_message(self, message: str):
        """Display a message in the component without triggering a solution expiration.

        Parameters
        ----------
        message
            Message to display.

        """

        def ui_callback():
            self.ghenv.Component.Message = message
            self.ghenv.Component.OnDisplayExpired(True)

        Rhino.RhinoApp.InvokeOnUiThread(System.Action(ui_callback))

    @classmethod
    def instance_by_component(
        cls,
        ghenv: "GhPython.Component.PythonEnvironment",
        long_running_function: Optional[Callable] = None,
        dispose_function: Optional[Callable] = None,
        auto_set_done: bool = True,
        force_new: bool = False,
        args=(),
    ):
        """Get the worker instance assigned to the component.

        This will get a persistant instance of a background worker
        for a given component. The parameter `force_new` can
        be set to `True` to request a new instance to be created.

        Parameters
        ----------
        ghenv
            Grasshopper environment object
        long_running_function
            This function will be the main entry point for the long-running task.
        dispose_function
            If defined, this function will be called when the worker is disposed.
            It can be used for clean-up tasks and resource deallocation.
        auto_set_done
            If true, the worker state will be automatically set to `Done` after the function returns.
            Defaults to `True`.
        force_new
            Force the creation of a new background worker, by default `False`.
        args : tuple, optional
            List or tuple of arguments for the invocation of the `long_running_function`. Defaults to `()`.

        Returns
        -------
        BackgroundWorker
            Instance of the background worker of the current component.
        """

        key = create_id(ghenv.Component, "background_worker")
        worker = scriptcontext.sticky.get(key)

        if worker and force_new:
            worker.request_cancellation()
            worker.dispose()
            worker = None
            del scriptcontext.sticky[key]

        if not worker:
            worker = cls(
                ghenv,
                long_running_function=long_running_function,
                dispose_function=dispose_function,
                auto_set_done=auto_set_done,
                args=args,
            )
            scriptcontext.sticky[key] = worker

        return worker

    @classmethod
    def stop_instance_by_component(cls, ghenv: "GhPython.Component.PythonEnvironment"):
        """Stops the worker instance assigned to the component.

        If there is no worker running, it will do nothing.

        Parameters
        ----------
        ghenv
            Grasshopper environment object
        """

        key = create_id(ghenv.Component, "background_worker")
        worker = scriptcontext.sticky.get(key)

        if worker:
            worker.request_cancellation()
            worker.dispose()
            worker = None
            del scriptcontext.sticky[key]
