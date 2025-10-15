import sys
from PySide6 import QtWidgets, QtCore

class LogStream(QtCore.QObject):
    """A custom stream to redirect stdout or stderr to a widget."""
    signal_error = QtCore.Signal()
    def __init__(self, log_widget, color="black"):
        super().__init__()
        self.log_widget = log_widget
        self.color = color

    def write(self, message):
        if message.strip():  # Ignore empty messages
            cursor = self.log_widget.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            if "[DEBUG]" in message:
                self.color = "blue"
            elif "[ERROR]" in message:
                self.color = "red"
                self.signal_error.emit()
            elif "[WARNING]" in message:
                self.color = "orange"
            else:
                self.color = "white"
            # self.textEdit.insertHtml(html)
            self.log_widget.insertHtml(
                f'<br><span style="color:{self.color}">{message}</span></br>')

    def flush(self):
        pass  # Flush is required by sys but can remain empty here

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