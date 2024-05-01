# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

### Changed

* Fix/add json serialization support to `Message` class.
* Fix get/set attr/item recursion bug. 
* Simplify API: 
  * Default to `Message` class if no message type is specified.
  * Allow to use a string with the topic name in place of an instance of `Topic`.
  * Added an `EchoSubscriber` to showcase basic usage.

### Removed


## [0.4.0] 2024-05-01

### Added

* Added the option to pass arguments into the long running task of a background worker.
* Added the option to manually control when the background worker task is set to **Done**.
* Added dispose function to control resource deallocation in a background worker.

### Changed

* Set background threads in the background worker as daemon threads to prevent blocking the main thread.
* Changed base class of `Message` from `UserDict` to `object` because in IronPython 2.7 `UserDict` is an old-style class. The behavior of dictionary-like is still preserved.

### Removed


## [0.3.7] 2024-04-03

### Added

### Changed

* Ensure calling `off()` or `unsubscribe()` does not fail if the callback is not present in the registered event callbacks.

### Removed


## [0.3.6] 2024-02-20

### Added

### Changed

* Fixed compatibility issues with COMPAS 2.0 on the background worker.

### Removed


## [0.3.5] 2024-02-11

### Added

### Changed

* Updated to COMPAS 2.0 theme
* Limit dependency on `mqtt-paho` to be `>=1, <2` since version `2.0` introduces breaking changes.

### Removed


## [0.3.4] 2023-11-24

### Added

### Changed

### Removed


## [0.3.3] 2023-11-24

### Added

### Changed

### Removed


## [0.3.2] 2023-11-24

### Added

### Changed

### Removed


## [0.3.1] 2023-11-24

### Added

### Changed

### Removed


## [0.3.0] 2023-11-01

### Added

* Added examples and more detailed documentation for installation and usage.
* Added `BackgroundWorker` class and `BackgroundTask` Grasshopper component to execute long-running tasks without blocking GH.

### Changed

* Fixed bug failing to get a `str` representation of `Message` on `ipy`
* Pinned Sphinx version for docs generation

### Removed


## [0.2.1] 2023-09-01

### Added

### Changed

### Removed


## [0.2.0] 2023-09-01

### Added

* Added support for callbacks directly on the base `Subscriber` class

### Changed

* Correctly implemented unsubscribe for all transports
* Fixed subscription with multiple subscribers on the same transport instance
* Switched to COMPAS data framework for encoding/decoding of messages

### Removed


## [0.1.2] 2023-07-09

### Added

### Changed

### Removed


## [0.1.1] 2023-07-09

### Added

### Changed

### Removed

