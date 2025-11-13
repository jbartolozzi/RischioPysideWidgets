import sys
import logging
from PySide6 import QtWidgets, QtCore

logger = logging.getLogger(__name__)

class LogStream(QtCore.QObject):
    """A custom stream to redirect stdout or stderr to a widget."""
    signal_error = QtCore.Signal()
    def __init__(self, log_widget, color="black"):
        super().__init__()
        self.log_widget = log_widget
        self.color = color

    def write(self, message):
        if message.strip():  # Ignore empty messages
            # Check if debug mode is enabled
            app = QtWidgets.QApplication.instance()
            cursor = self.log_widget.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            if "DEBUG" in message:
                self.color = "blue"
            elif "ERROR" in message:
                self.color = "red"
                self.signal_error.emit()
            elif "WARNING" in message:
                self.color = "orange"
            else:
                self.color = "white"
            # self.textEdit.insertHtml(html)
            self.log_widget.insertHtml(
                f'<br><span style="color:{self.color}">{message}</span></br>')

    def flush(self):
        pass  # Flush is required by sys but can remain empty here


class QtLogHandler(logging.Handler, QtCore.QObject):
    """Custom logging handler that outputs to both terminal and Qt widget."""

    # Signal to emit log messages to the main thread
    log_message_signal = QtCore.Signal(str, str)

    def __init__(self, log_widget, also_log_to_console=True):
        logging.Handler.__init__(self)
        QtCore.QObject.__init__(self)
        self.log_widget = log_widget
        self.also_log_to_console = also_log_to_console

        # Store original stdout for console output
        self.console_stdout = sys.__stdout__
        self.console_stderr = sys.__stderr__

        # Connect signal to slot for thread-safe GUI updates
        self.log_message_signal.connect(self._append_to_widget, QtCore.Qt.QueuedConnection)

    def _append_to_widget(self, msg, color):
        """Slot to append message to widget (runs on main thread)."""
        try:
            cursor = self.log_widget.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.log_widget.insertHtml(
                f'<br><span style="color:{color}">{msg}</span></br>')
        except Exception as e:
            # Fail silently if widget is being destroyed
            pass

    def emit(self, record):
        try:
            # Format the log message
            msg = self.format(record)

            # Output to console if running from terminal
            if self.also_log_to_console:
                if record.levelno >= logging.ERROR:
                    print(msg, file=self.console_stderr)
                else:
                    print(msg, file=self.console_stdout)

            # Map logging levels to colors
            level_colors = {
                logging.DEBUG: "blue",
                logging.INFO: "white",
                logging.WARNING: "orange",
                logging.ERROR: "red",
                logging.CRITICAL: "red"
            }
            color = level_colors.get(record.levelno, "white")

            # Emit signal to update GUI on main thread
            self.log_message_signal.emit(msg, color)

        except Exception:
            self.handleError(record)


class LogWindow(QtWidgets.QDialog):

    signal_error = QtCore.Signal()
    signal_clear = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thickness Log")
        self.resize(600, 400)

        # Set up layout and log display area
        layout = QtWidgets.QVBoxLayout()
        self.log_text_edit = QtWidgets.QTextEdit(self)
        self.log_text_edit.setStyleSheet("background-color: black;")
        self.log_text_edit.setReadOnly(True)
        # Disable word wrap
        self.log_text_edit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        layout.addWidget(self.log_text_edit)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # Add a debug mode checkbox
        self.debug_checkbox = QtWidgets.QCheckBox("Enable Debug Logging", self)
        # Check current logging level to set initial checkbox state
        root_logger = logging.getLogger()
        self.debug_checkbox.setChecked(root_logger.level == logging.DEBUG)
        self.debug_checkbox.stateChanged.connect(self.toggle_debug_mode)

        # Add a copy to clipboard button
        copy_button = QtWidgets.QPushButton("Copy to Clipboard", self)
        copy_button.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(self.log_text_edit.toPlainText()))

        # Add a save to txt file button
        save_button = QtWidgets.QPushButton("Save to File", self)
        save_button.clicked.connect(self.save_to_file)

        # Add a button to close the dialog
        close_button = QtWidgets.QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        # layout.addWidget(close_button)

        button_widget = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.debug_checkbox)
        button_layout.addWidget(copy_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)
        button_widget.setLayout(button_layout)

        layout.addWidget(button_widget)

        self.setLayout(layout)

        # Redirect stdout and stderr
        self.stdout_stream = LogStream(self.log_text_edit, "white")
        self.stderr_stream = LogStream(self.log_text_edit, "red")
        self.stderr_stream.signal_error.connect(self.signal_error.emit)

        sys.stdout = self.stdout_stream
        sys.stderr = self.stderr_stream

        # Set up logging handler
        self.setup_logging()

    def setup_logging(self):
        """Set up logging to output to both console and log window."""
        # Create and configure the custom handler
        self.log_handler = QtLogHandler(self.log_text_edit, also_log_to_console=True)

        # Set the format for log messages
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.log_handler.setFormatter(formatter)

        # Get the root logger and add our handler
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)

        # Note: logging level is set in app.py based on --debug flag
        # The checkbox state is synced with the current logging level

    def toggle_debug_mode(self, state):
        """Toggle debug mode on or off."""
        debug_enabled = state == QtCore.Qt.CheckState.Checked.value
        # Update logging level
        root_logger = logging.getLogger()
        if debug_enabled:
            root_logger.setLevel(logging.DEBUG)
            logger.info("Debug logging enabled")
        else:
            root_logger.setLevel(logging.INFO)
            logger.info("Debug logging disabled")

    def append_html(self, message):
        """Appends HTML-formatted text to the log."""
        self.log_text_edit.moveCursor(QtCore.Qt.TextCursor.End)
        self.log_text_edit.insertHtml(message)
        # Adds a newline after each message
        self.log_text_edit.insertPlainText("\n")
        self.log_text_edit.moveCursor(QtCore.Qt.TextCursor.End)

    def closeEvent(self, event):
        # Restore stdout and stderr when the dialog is closed
        # sys.stdout = sys.__stdout__
        # sys.stderr = sys.__stderr__
        event.accept()

    def save_to_file(self):
        """Save the log to a text file."""
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Log", "", "Text Files (*.txt)")
        if file_name:
            with open(file_name, "w") as file:
                file.write(self.log_text_edit.toPlainText())

    def show(self):
        self.signal_clear.emit()
        super().show()