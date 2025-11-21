# RischioPysideWidgets

A collection of reusable PySide6 widgets and utilities for building Qt-based Python applications.

## Installation

```bash
# Clone the repository
git clone git@github.com:jbartolozzi/RischioPysideWidgets.git

# Install dependencies
pip install PySide6
```

## Modules

### core

Core utilities and application-wide functions.

#### Functions

**`resourcePath(relative_path: str) -> str`**

Returns the absolute path to a resource file. Handles PyInstaller bundled applications by checking for `sys._MEIPASS`.

```python
from RischioPysideWidgets.core import resourcePath

icon_path = resourcePath('icons/rischio.png')
```

**`get_app_settings() -> QSettings`**

Returns a QSettings instance configured with organization "rischio" and the current application name.

```python
from RischioPysideWidgets.core import get_app_settings

settings = get_app_settings()
settings.setValue("theme", "dark")
```

**`reset_settings()`**

Clears all application settings.

**`get_setting(key: str, default=None) -> Any`**

Retrieves a setting value by key, returning the default if not found.

```python
from RischioPysideWidgets.core import get_setting

theme = get_setting("theme", "light")
```

**`runCommand(command, detach=False, env=None) -> Union[int, tuple]`**

Executes a shell command. Returns process ID if detached, or (stdout, stderr, return_code) tuple if synchronous.

```python
from RischioPysideWidgets.core import runCommand

# Synchronous execution
output, error, code = runCommand("ls -la")

# Detached execution
pid = runCommand("python server.py", detach=True)
```

**`set_dark_palette(app: QApplication)`**

Applies a dark Fusion theme to the application.

```python
from PySide6.QtWidgets import QApplication
from RischioPysideWidgets.core import set_dark_palette

app = QApplication([])
set_dark_palette(app)
```

---

### about

About dialog widget for displaying application information.

#### Classes

**`AboutDialog(parent=None, open_source_projects=None)`**

A dialog displaying application name, version, icon, and optional third-party library credits.

**Parameters:**
- `parent` (QWidget, optional): Parent widget
- `open_source_projects` (list, optional): List of dicts with 'name' and 'url' keys, or tuples of (name, url)

**Requirements:**
- Application name must be set via `QCoreApplication.applicationName()`
- Application version must be set via `QCoreApplication.applicationVersion()`
- Icon expected at `icons/rischio.png` (via `resourcePath()`)

```python
from PySide6.QtCore import QCoreApplication
from RischioPysideWidgets.about import AboutDialog

QCoreApplication.setApplicationName("MyApp")
QCoreApplication.setApplicationVersion("1.0.0")

projects = [
    {'name': 'PySide6', 'url': 'https://wiki.qt.io/Qt_for_Python'},
    ('NumPy', 'https://numpy.org/')
]

dialog = AboutDialog(open_source_projects=projects)
dialog.exec()
```

---

### helpers

Custom widgets and UI helper functions.

#### Functions

**`notify_user(title: str, message: str) -> QMessageBox`**

Displays a modal message box and returns the QMessageBox instance.

**`show_message(title: str, message: str, parent=None) -> QMessageBox`**

Displays a message box with optional parent widget.

**`set_fixed_label_size(label: QLabel, sample_text: str)`**

Sets a fixed minimum size for a QLabel based on sample text width.

#### Classes

**`FocusReleaseSpinBox`**

A QSpinBox that clears focus when Enter/Return is pressed.

```python
from RischioPysideWidgets.helpers import FocusReleaseSpinBox

spinbox = FocusReleaseSpinBox()
spinbox.valueChanged.connect(lambda val: print(f"Value: {val}"))
```

**`FilePicker(label=None, placeholder_text=None, filepath_root=None, is_directory=False, parent=None)`**

A widget combining a QLineEdit and browse button for file/directory selection.

**Signals:**
- `textChanged(str)`: Emitted when the file path changes

**Methods:**
- `text() -> str`: Returns the current file path
- `setText(text: str)`: Sets the file path
- `fileExists() -> bool`: Returns True if the selected path exists

```python
from RischioPysideWidgets.helpers import FilePicker

picker = FilePicker(
    label="Select Model",
    placeholder_text="Choose a .pth file",
    filepath_root="/home/user/models",
    is_directory=False
)
picker.textChanged.connect(lambda path: print(f"Selected: {path}"))
```

**`CommandWorker(command, title, message, parent=None)`**

A dialog that runs a shell command in a background thread with a progress bar.

**Parameters:**
- `command` (str): Shell command to execute
- `title` (str): Dialog window title
- `message` (str): Message to display

```python
from RischioPysideWidgets.helpers import CommandWorker

dialog = CommandWorker(
    command="pip install requests",
    title="Installing",
    message="Installing dependencies..."
)
dialog.exec()
```

**`BlinkButton(text: str = "", parent=None)`**

A QPushButton with glow and blink animation effects.

**Methods:**
- `enable_glow(color: str = "cyan", blur_radius: int = 18)`: Turns on steady glow
- `disable_glow()`: Turns off glow
- `blink(duration_ms: int = 2000, interval_ms: int = 250, color: str = "yellow", blur_radius: int = 18)`: Blinks for specified duration

```python
from RischioPysideWidgets.helpers import BlinkButton

button = BlinkButton("Click Me")
button.clicked.connect(lambda: button.blink(duration_ms=1000, color="green"))
```

---

### loading

Loading dialogs for long-running operations with animations.

#### Classes

**`Worker(operation, *args, **kwargs)`**

A QThread worker for running background operations.

**Signals:**
- `finished()`: Emitted when operation completes
- `progress(int)`: Emitted for progress updates
- `error(str)`: Emitted on error
- `result(object)`: Emitted with operation result

```python
from RischioPysideWidgets.loading import Worker

def long_task(x, y):
    return x + y

worker = Worker(long_task, 5, 10)
worker.result.connect(lambda res: print(f"Result: {res}"))
worker.start()
```

**`LoadingDialog(parent=None, message="Loading...")`**

A frameless loading dialog with progress bar and animated dots.

**Methods:**
- `set_message(message: str)`: Updates the loading message

```python
from RischioPysideWidgets.loading import LoadingDialog, Worker

dialog = LoadingDialog(message="Processing data...")
worker = Worker(some_long_operation)
worker.finished.connect(dialog.close)
worker.start()
dialog.exec()
```

**`SpinnerDialog(parent=None, message="Processing...")`**

A frameless loading dialog with custom painted spinner animation.

**Methods:**
- `set_message(message: str)`: Updates the message

```python
from RischioPysideWidgets.loading import SpinnerDialog, Worker

dialog = SpinnerDialog(message="Analyzing...")
worker = Worker(analysis_function)
worker.finished.connect(dialog.close)
worker.start()
dialog.exec()
```

---

### logview

Logging window with GUI integration and thread-safe logging.

#### Classes

**`LogStream(log_widget, color="black")`**

A custom stream to redirect stdout/stderr to a QTextEdit widget.

**Signals:**
- `signal_error()`: Emitted when ERROR level messages are logged

**`QtLogHandler(log_widget, also_log_to_console=True)`**

A thread-safe logging.Handler that outputs to both terminal and Qt widget.

**Signals:**
- `log_message_signal(str, str)`: Emitted with (message, color)

**`LogWindow()`**

A dialog that displays color-coded logs with debug mode toggle.

**Signals:**
- `signal_error()`: Emitted when errors are logged
- `signal_clear()`: Emitted when window is shown

**Methods:**
- `append_html(message: str)`: Appends HTML-formatted text to the log

```python
import logging
from RischioPysideWidgets.logview import LogWindow

log_window = LogWindow()
log_window.show()

logger = logging.getLogger(__name__)
logger.info("Application started")
logger.error("Something went wrong")
```

---

### threaded_loading_dialog

Generic dialog for executing task queues in background threads.

#### Classes

**`TaskWorkerThread(tasks, parent=None)`**

Worker thread that executes a queue of tasks sequentially.

**Signals:**
- `task_started(int, str)`: Emitted with (task_index, description)
- `task_completed(int)`: Emitted with task_index
- `all_completed(object)`: Emitted with results list
- `error(str)`: Emitted with error message
- `progress(int, int)`: Emitted with (current, total)

**Task Format:**
Each task is a dictionary with:
- `function` (callable): Function to execute
- `description` (str): Description for UI
- `args` (tuple, optional): Positional arguments
- `kwargs` (dict, optional): Keyword arguments

**`ThreadedLoadingDialog(parent=None, title="Processing", tasks=None)`**

A generic loading dialog that runs tasks in a background thread with progress tracking.

**Methods:**
- `set_tasks(tasks: list)`: Sets the task queue
- `set_on_complete_callback(callback)`: Sets completion callback
- `set_on_error_callback(callback)`: Sets error callback
- `set_auto_close(enabled: bool, delay: int = 800)`: Configures auto-close behavior
- `start()`: Starts executing tasks
- `execute() -> int`: Starts tasks and shows dialog (blocking), returns dialog result
- `set_status(text: str)`: Updates status label
- `set_error(error_message: str = None)`: Displays error state
- `set_complete()`: Displays completion state

```python
from RischioPysideWidgets.threaded_loading_dialog import ThreadedLoadingDialog

def process_data(data):
    # Process data
    return result

def save_results(results):
    # Save to file
    pass

tasks = [
    {
        'function': process_data,
        'description': 'Processing data...',
        'args': (my_data,)
    },
    {
        'function': save_results,
        'description': 'Saving results...',
        'kwargs': {'results': processed_data}
    }
]

dialog = ThreadedLoadingDialog(parent=self, title="Processing", tasks=tasks)
dialog.set_on_complete_callback(lambda results: print("Done!", results))
dialog.set_on_error_callback(lambda err: print("Error:", err))
dialog.execute()
```

---

## Examples

See the `if __name__ == '__main__'` sections in each module for working examples:

```bash
python about.py
python loading.py
python threaded_loading_dialog.py
```

## Dark Theme

All widgets are designed for dark theme applications. Apply the dark palette to your app:

```python
from PySide6.QtWidgets import QApplication
from RischioPysideWidgets.core import set_dark_palette

app = QApplication([])
set_dark_palette(app)
# ... rest of your app
app.exec()
```

## License

© 2025 Studio Rischio LLC
