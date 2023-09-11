"""
Background Task component.

Executes a long-running task in the background, while keeping Grasshopper reactive.

COMPAS EVE v0.2.1
"""
import time

from compas_eve.ghpython import BackgroundWorker
from ghpythonlib.componentbase import executingcomponent as component


def do_work(worker):
    # This is an example of how to write a long-running task
    # Replace the content of this function with your own, the only thing important
    # to keep in mind is to leave the calls set_internal_state_to_* in all the right places

    # 1. Call this function at the start of your long-running task to notify you have started
    worker.set_internal_state_to_working()
    worker.display_message("Starting task...")
    time.sleep(0.5)

    # 2. Result can be of any data type
    result = 0

    # 3. Do something long-running
    for i in range(50):

        # 4. Handle cancellation requests during your long-running task
        if worker.has_requested_cancellation():
            worker.display_message("Cancelled")
            worker.set_internal_state_to_cancelled()
            break

        worker.current_value = i
        result += i
        worker.display_progress(i / (50 - 1))
        time.sleep(0.01)

    # 5. Set to done, including the result contents
    worker.set_internal_state_to_done(result)


class BackgroundTaskComponent(component):
    def RunScript(self, start):
        self.worker = BackgroundWorker.instance_by_component(ghenv, do_work, force_new=start)  # noqa: F821

        if not self.worker.is_working() and not self.worker.is_done() and start:
            self.worker.start_work()

        print("Is worker working? {}".format(self.worker.is_working()))
        print("Is worker done? {}".format(self.worker.is_done()))

        if self.worker.is_done():
            print("Completed")

        if hasattr(self.worker, "result"):
            return (self.worker.result,)
        else:
            return (None,)
