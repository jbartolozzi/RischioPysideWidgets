import os
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QFontMetrics
from .core import runCommand, log_info, log_error


def notify_user(title, message):
    msg_box = QtWidgets.QMessageBox()  # Create a new QMessageBox
    msg_box.setWindowTitle(title)  # Set the title for the message box
    msg_box.setText(message)  # Set the text for the message box
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)  # Add an OK button to the message box
    msg_box.exec()  # Execute the message box
    return msg_box

def show_message(title, message, parent=None):
    msg_box = QtWidgets.QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.exec()
    return msg_box

class FocusReleaseSpinBox(QtWidgets.QSpinBox):
    def keyPressEvent(self, event):
        """Clear focus when Enter is pressed."""
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.clearFocus()  # Remove focus from SpinBox
        else:
            super().keyPressEvent(event)  # Default behavior

def set_fixed_label_size(label, sample_text):
    """Sets a fixed size hint for QLabel based on sample text width."""
    font_metrics = QFontMetrics(label.font())
    text_width = font_metrics.boundingRect(sample_text).width()
    text_height = font_metrics.boundingRect(sample_text).height()

    # Set minimum size to fit the widest possible text
    label.setMinimumSize(text_width, text_height)

class FilePicker(QtWidgets.QWidget):
    textChanged = QtCore.Signal(str)

    def __init__(self,
                 label=None,
                 placeholder_text=None,
                 filepath_root=None,
                 is_directory=False,
                 parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.is_directory = is_directory
        self.button = QtWidgets.QPushButton("Select File" if label is None else label)
        self.button.clicked.connect(self.open_file_dialog)
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setFixedWidth(250)
        if placeholder_text is None:
            self.line_edit.setPlaceholderText("Select File")
        else:
            self.line_edit.setPlaceholderText(placeholder_text)
        self.line_edit.textChanged.connect(self.updateLabel)
        self.status_label = QtWidgets.QLabel()
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.line_edit)
        hbox.addWidget(self.button)
        self.filepath_root = filepath_root
        self.setLayout(hbox)
        self.updateLabel("")


    def open_file_dialog(self):
        file_dialog = QtWidgets.QFileDialog(self)
        if self.filepath_root is not None and os.path.exists(self.filepath_root):
            file_dialog.setDirectory(self.filepath_root)

        # Only allow selecting existing files
        file_dialog.setFileMode(
            QtWidgets.QFileDialog.Directory if self.is_directory else QtWidgets.QFileDialog.ExistingFile)
        # file_dialog.setNameFilter(f"(*{self.file_type_filter})")  # Optional filter for file types
        if file_dialog.exec():
            self.selected_file = file_dialog.selectedFiles()[0]
            if self.selected_file is not None:
                self.line_edit.setText(self.selected_file)
            else:
                self.line_edit.clear()
        # This is called because we are listening for text changed
        # self.updateLabel()

    def updateLabel(self, current_text):
        if current_text.strip() == "":
            icon_name = "SP_FileIcon"
        elif os.path.exists(current_text):
            icon_name = "SP_DialogApplyButton"
        else:
            icon_name = "SP_MessageBoxWarning"
        icon = self.style().standardIcon(getattr(QtWidgets.QStyle, icon_name))
        # Set the icon to the label
        self.status_label.setPixmap(icon.pixmap(32, 32))  # Adjust the size as needed=
        self.textChanged.emit(current_text)

    def text(self):
        return self.line_edit.text()

    def setText(self, text):
        self.line_edit.setText(text)

    def fileExists(self):
        return os.path.exists(self.line_edit.text())


class CommandWorker(QtWidgets.QDialog):
    class Worker(QObject):
        complete = Signal(str, str, int)

        def __init__(self, command):
            super().__init__()
            self.command = command

        def run(self):
            out, err, code = runCommand(self.command)
            self.complete.emit(out, err, code)

    """A Qt dialog that runs a command and shows a progress bar."""
    def __init__(self, command, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Running Command")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setFixedSize(300, 150)

        # UI Components
        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel(message)
        self.label.setWordWrap(True)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        print("Command: ", command)
        self.thread_run = QtCore.QThread()

        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

        self.worker = CommandWorker.Worker(command)
        self.worker.moveToThread(self.thread_run)
        self.worker.complete.connect(self.complete)
        self.thread_run.started.connect(self.worker.run)
        self.thread_run.start()

    def exec(self):
        """Show the dialog and start the command."""
        super().exec()
        self.thread_run.quit()
        self.thread_run.wait()
        self.close()

    def cancel(self):
        """Cancel the command."""
        print("Cancelling command")
        self.thread_run.exit()
        self.thread_run.wait()
        self.close()

    def complete(self, out, err, code):
        print("Command complete")
        """Handle the completion of the command."""
        log_info(out)
        if code != 0:
            log_error(err)
        self.thread_run.quit()
        self.thread_run.wait()
        self.close()
