# COMPAS EVE
Event-based communication framework for the COMPAS ecosystem, providing publisher/subscriber messaging with support for in-memory, MQTT, and Rhino/Grasshopper integrations.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively
- Bootstrap and install development dependencies:
  - `pip install -e .[dev]` -- installs all dev tools and the package in editable mode. Takes ~60 seconds with good network.
  - **NOTE**: May fail in environments with restricted network access. If pip times out, dependencies may need manual installation.
- **NEVER CANCEL**: Set timeout to 300+ seconds for dependency installation in case of slow network.
- `invoke clean` -- clean all generated artifacts. Takes ~1 second.
- `invoke lint` -- run flake8 and black linters. Takes ~1 second.
- `invoke format` -- reformat code with black. Takes ~1 second.  
- `invoke check` -- comprehensive style and metadata checks. Takes ~2 seconds.
- `invoke docs` -- build HTML documentation with Sphinx. Takes ~7 seconds.
- **Unit tests only**: `pytest tests/unit` -- run core unit tests. Takes ~0.5 seconds.
- **Full tests**: `invoke test` or `pytest` -- runs ALL tests including integration tests. Integration tests will FAIL without MQTT broker setup.

## Testing Requirements
- **Unit tests**: Work immediately after installation. Test core event messaging functionality.
- **Integration tests**: Require MQTT broker running on localhost:1883.
  - Set up MQTT broker: `docker run -d --name nanomq -p 1883:1883 emqx/nanomq:latest`  
  - **IMPORTANT**: Change `HOST = "broker.hivemq.com"` to `HOST = "localhost"` in `tests/integration/test_mqtt.py`
  - Run tests: `pytest tests/integration` -- takes ~4 seconds with local broker
  - Clean up: `docker rm -f nanomq`
  - Integration tests validate MQTT transport functionality
  - **NEVER CANCEL**: Integration tests may take 5+ seconds to start broker and run tests.

## Validation
- Always run `invoke clean && invoke lint && invoke format && invoke check` before committing changes.
- **VALIDATION SCENARIOS**: Test basic functionality after changes:
  - `python -m compas_eve` -- should print "COMPAS EVE v1.0.0 is installed!"
  - `python docs/examples/01_hello_world.py` -- should print publisher/subscriber message exchange 
- Always manually test examples in `docs/examples/` when changing core functionality.
- The CI will run tests on Windows, macOS, Linux with Python 3.9, 3.10, 3.11 AND IronPython 2.7.

## Installation & Dependencies
- **Python Requirements**: Python 3.8+ (supports CPython and IronPython)
- **Core Dependencies**: compas>=1.17.6, paho-mqtt
- **Development Tools**: invoke, pytest, black, flake8, sphinx
- **Development Installation**: `pip install -e .[dev]` (installs package in editable mode)

## Code Style & Documentation
- **Docstring Style**: Use numpy-style docstrings for all functions, classes, and methods
- **Code Formatting**: Use `invoke format` to automatically format code with black
- **Linting**: Use `invoke lint` to check code style with flake8 and black
- **Type Hints**: Include type hints where appropriate for better code clarity

## Build System
- Uses **setuptools** with `setup.py` and modern `pyproject.toml`
- **invoke** task runner for automation (replaces Make/scripts)
- **pytest** for testing with doctest integration
- **Sphinx** for documentation with `sphinx_compas2_theme`
- No compiled components - pure Python package

## Common Tasks
The following are outputs from frequently run commands. Reference them instead of running bash commands to save time.

### Repository root structure
```
├── .github/           # GitHub Actions workflows  
├── docs/              # Sphinx documentation
├── src/compas_eve/    # Main package source
│   ├── core.py        # Core messaging classes
│   ├── memory/        # In-memory transport
│   ├── mqtt/          # MQTT transport
│   ├── ghpython/      # Grasshopper components (not used in CI)
│   └── rhino/         # Rhino integration (not used in CI)
├── tests/
│   ├── unit/          # Fast unit tests (no external deps)
│   └── integration/   # MQTT integration tests
├── requirements.txt   # Runtime dependencies
├── requirements-dev.txt # Development dependencies  
├── setup.py          # Package configuration
├── pyproject.toml    # Modern Python project config
└── tasks.py          # Invoke task definitions
```

### Key source files
- `src/compas_eve/core.py` -- Main Message, Publisher, Subscriber, Topic classes
- `src/compas_eve/memory/` -- InMemoryTransport for single-process messaging  
- `src/compas_eve/mqtt/` -- MqttTransport for distributed messaging
- `src/compas_eve/ghpython/` -- Grasshopper background task components (not used in CI)
- `tests/unit/test_core.py` -- Core functionality unit tests
- `tests/integration/test_mqtt.py` -- MQTT transport integration tests

### Package imports and usage
```python
import compas_eve as eve

# In-memory messaging (default)
pub = eve.Publisher("/topic")  
sub = eve.EchoSubscriber("/topic")
sub.subscribe()
pub.publish({"message": "hello"})

# MQTT messaging  
from compas_eve.mqtt import MqttTransport
eve.set_default_transport(MqttTransport("broker.hivemq.com"))
```

## Special Features
- **Multiple Transports**: In-memory (default), MQTT for distributed systems
- **IronPython Support**: Full compatibility with IronPython 2.7 for legacy environments
- **Cross-platform**: Windows, macOS, Linux support

## Timing Expectations
- Package installation: ~60 seconds with good network, may timeout in restricted environments (**NEVER CANCEL** - set 300+ second timeout)
- Unit tests: ~0.5 seconds
- Integration tests: ~4 seconds (including MQTT broker communication)
- Linting/formatting: ~1 second each  
- Documentation build: ~7 seconds
- **NEVER CANCEL any build or test commands** - they are generally fast but may have network or startup overhead

## CI/CD Integration
- GitHub Actions workflows in `.github/workflows/`
- Tests run on multiple OS/Python combinations
- **Always run** `invoke lint` before pushing - CI enforces code style
- Uses `compas-dev/compas-actions.build@v4` for standard COMPAS project workflows