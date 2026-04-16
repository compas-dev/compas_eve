try:
    import Grasshopper  # type: ignore
except (ImportError, SyntaxError):
    pass

from .background import BackgroundWorker


def warning(component: "Grasshopper.Kernel.IGH_Component", message: str):
    """Add a warning message to the component.

    Parameters
    ----------
    component
        The component instance. Use `ghenv.Component`.
    message
        The message to display.
    """
    component.AddRuntimeMessage(Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning, message)


def error(component: "Grasshopper.Kernel.IGH_Component", message: str):
    """Add an error message to the component.

    Parameters
    ----------
    component
        The component instance. Pre-Rhino8 use `self`. Post-Rhino8 use `ghenv.Component`.
    message
        The message to display.
    """
    component.AddRuntimeMessage(Grasshopper.Kernel.GH_RuntimeMessageLevel.Error, message)


def remark(component: "Grasshopper.Kernel.IGH_Component", message: str):
    """Add a remark message to the component.

    Parameters
    ----------
    component
        The component instance. Pre-Rhino8 use `self`. Post-Rhino8 use `ghenv.Component`.
    message
        The message to display.
    """
    component.AddRuntimeMessage(Grasshopper.Kernel.GH_RuntimeMessageLevel.Remark, message)


def message(component: "Grasshopper.Kernel.IGH_Component", message: str):
    """Add a text that will appear under the component.

    Parameters
    ----------
    component
        The component instance. Pre-Rhino8 use `self`. Post-Rhino8 use `ghenv.Component`.
    message
        The message to display.
    """
    component.Message = message


__all__ = ["BackgroundWorker", "warning", "error", "remark", "message"]
