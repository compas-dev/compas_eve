# Installation

This chapter provides a step-by-step guide for installing `compas_eve` on your system.
We highly recommend using [uv](https://docs.astral.sh/uv/) for managing
your Python environment and dependencies, as it is significantly faster and
more reliable. Alternatively, you can simply use standard `pip` or `conda`.

## Install uv

If you do not have `uv` installed, follow the instructions on their website or run:

=== "Mac/Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

## Create a virtual environment

It is best practice to install `compas_eve` in a virtual environment.
Navigate to your project directory and run:

```bash
uv venv
```

This creates a virtual environment in `.venv`. Activate it with:

=== "Mac/Linux"

    ```bash
    source .venv/bin/activate
    ```

=== "Windows"

    ```powershell
    .venv\Scripts\activate
    ```

## Install compas_eve

With your virtual environment activated, install `compas_eve`:

```bash
uv pip install compas_eve
```

## Verify installation

Verify that `compas_eve` is available:

```bash
python -m compas_eve
```

If the version number is printed, the installation is complete.

## Install for Rhino

COMPAS EVE is compatible with Rhino 8 and later versions. 

### Rhino Script Editor

To use `compas_eve` in a Python script, simply add the requirement header to the top of your script in the Rhino 8 Script Editor:

```python
# r: compas_eve
```
### Grasshopper

To use `compas_eve` Grasshopper components, open the `Package Manager`, search for `compas_eve` and click `Install`.

## Transports

Depending on the transport you want to use, you might need to install additional dependencies.

### MQTT Transport

The `MQTT` transport is the default option and is installed automatically with `compas_eve`. 

### Zenoh Transport

The `Zenoh` transport requires the `eclipse-zenoh` package, which is an optional dependency.
To install it, run:

```bash
uv pip install compas_eve[zenoh]
```

For more details about Zenoh, refer to the [Eclipse Zenoh](https://zenoh.io/) website.
