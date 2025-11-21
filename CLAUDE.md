# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RischioPysideWidgets is a shared widget library for PySide6 applications developed by Studio Rischio LLC. It provides reusable UI components, utilities, and helpers for building Qt-based Python applications.

## Development Environment

This project uses Conda for Python environment management (see `.vscode/settings.json`).

## Architecture

### Module Structure

This is a flat package structure with focused modules:

- **[core.py](core.py)** - Core utilities and application-wide functions
  - Settings management using QSettings with "rischio" organization name
  - Resource path handling for PyInstaller bundled apps (`resourcePath()`)
  - Command execution via `runCommand()` (supports detached processes)
  - Dark theme palette via `set_dark_palette()`

- **[about.py](about.py)** - `AboutDialog` widget
  - Displays app name/version from `QCoreApplication.applicationName/Version()`
  - Expects `icons/rischio.png` icon via `core.resourcePath()`
  - Supports optional third-party library credits (`open_source_projects` parameter)
  - Auto-sizes based on number of projects listed

- **[helpers.py](helpers.py)** - Custom widgets and UI helpers
  - `FilePicker` - File/directory selection widget with validation indicators
  - `FocusReleaseSpinBox` - QSpinBox that releases focus on Enter key
  - `CommandWorker` - Dialog for running commands in background threads
  - `BlinkButton` - QPushButton with glow/blink animation effects
  - `notify_user()` and `show_message()` - Message box helpers

- **[loading.py](loading.py)** - Loading dialogs for long-running operations
  - `Worker` - QThread-based worker for background operations
  - `LoadingDialog` - Progress bar with animated dots
  - `SpinnerDialog` - Custom painted spinner animation
  - Both dialogs use dark theme styling and frameless windows

- **[logview.py](logview.py)** - Logging window with GUI integration
  - `LogWindow` - QDialog that displays logs with color-coded levels
  - `LogStream` - Redirects stdout/stderr to QTextEdit widget
  - `QtLogHandler` - Thread-safe logging.Handler for Qt widgets
  - Supports debug mode toggle, copy to clipboard, and save to file

- **[threaded_loading_dialog.py](threaded_loading_dialog.py)** - Generic task queue dialog
  - `ThreadedLoadingDialog` - Executes multiple tasks sequentially in background
  - `TaskWorkerThread` - Worker that processes task queue with progress tracking
  - Tasks defined as dicts with `function`, `description`, `args`, `kwargs`
  - Cancellable with error handling and auto-close on completion

### Key Design Patterns

**Application Settings:**
All settings use the "rischio" organization name via `core.get_app_settings()`. Application name is set via `QCoreApplication.applicationName()`.

**Threading:**
All background operations use QThread-based workers with Signal/Slot communication:
- Workers emit signals (finished, error, result, progress)
- Main thread connects slots before calling `worker.start()`
- Always call `thread.quit()` and `thread.wait()` for cleanup

**Resource Paths:**
Use `core.resourcePath()` for all resource files to support PyInstaller bundling (checks for `sys._MEIPASS`).

**Dark Theme:**
Widgets in this library assume dark theme usage. Apply via `core.set_dark_palette(app)` or use inline StyleSheets.

## Common Tasks

**Adding a new reusable widget:**
1. Add to [helpers.py](helpers.py) if it's a simple custom widget
2. Create new module if it's complex with multiple classes (like loading dialogs)
3. Follow existing patterns: inherit from Qt widgets, use Signal/Slot for events
4. Include dark theme styling if applicable

**Testing widgets:**
Most modules include `if __name__ == '__main__'` sections with working examples. Run directly:
```bash
python about.py
python loading.py
python threaded_loading_dialog.py
```

**Using the CommandWorker:**
```python
from .helpers import CommandWorker
dialog = CommandWorker(command="ls -la", title="Running", message="Listing files...")
dialog.exec()
```

**Using ThreadedLoadingDialog:**
```python
from .threaded_loading_dialog import ThreadedLoadingDialog

tasks = [
    {'function': my_func, 'description': 'Processing data...', 'args': (arg1,), 'kwargs': {'key': 'value'}},
    {'function': another_func, 'description': 'Finalizing...'}
]
dialog = ThreadedLoadingDialog(parent=self, title="Processing", tasks=tasks)
dialog.set_on_complete_callback(lambda results: print(results))
dialog.execute()
```

## Important Notes

- The `__init__.py` file is currently empty - widgets must be imported directly from their modules
- LogWindow redirects sys.stdout/sys.stderr - only one instance should be active
- AboutDialog expects the icon at `icons/rischio.png` via resourcePath
- All QThread workers should be properly cleaned up with quit() and wait() to prevent crashes
