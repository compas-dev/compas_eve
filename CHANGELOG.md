# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

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

