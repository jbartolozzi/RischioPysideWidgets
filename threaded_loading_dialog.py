"""
Threaded Loading Dialog - A generic dialog for running tasks in a background thread
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton
from PySide6.QtCore import QThread, Signal, Qt, QTimer


class TaskWorkerThread(QThread):
    """Worker thread that executes a queue of tasks sequentially"""

    task_started = Signal(int, str)  # (task_index, description)
    task_completed = Signal(int)      # task_index
    all_completed = Signal(object)    # result_data
    error = Signal(str)               # error_message
    progress = Signal(int, int)       # (current, total)

    def __init__(self, tasks, parent=None):
        """
        Initialize the worker thread

        Args:
            tasks: List of dictionaries with keys:
                - 'function': callable to execute
                - 'description': str description for UI
                - 'args': tuple of positional arguments (optional)
                - 'kwargs': dict of keyword arguments (optional)
        """
        super().__init__(parent)
        self.tasks = tasks
        self._is_cancelled = False
        self.results = []

    def run(self):
        """Execute all tasks in sequence"""
        func = None
        try:
            total_tasks = len(self.tasks)

            for i, task in enumerate(self.tasks):
                if self._is_cancelled:
                    return

                # Emit task started
                description = task.get('description', f'Task {i+1}')
                self.task_started.emit(i, description)
                self.progress.emit(i, total_tasks)

                # Execute the task
                func = task['function']
                args = task.get('args', ())
                kwargs = task.get('kwargs', {})

                result = func(*args, **kwargs)
                self.results.append(result)

                if self._is_cancelled:
                    return

                # Emit task completed
                self.task_completed.emit(i)

            # All tasks completed successfully
            self.progress.emit(total_tasks, total_tasks)
            self.all_completed.emit(self.results)

        except Exception as e:
            # Emit the error message with the currently running task and the exception details
            self.error.emit(f"Error:{str(func)} {str(e)}")

    def cancel(self):
        """Request cancellation of the task queue"""
        self._is_cancelled = True


class ThreadedLoadingDialog(QDialog):
    """
    Generic loading dialog that runs tasks in a background thread

    Features:
    - Runs a queue of tasks sequentially in a background thread
    - Shows progress and current task description
    - Cancellable
    - Error handling with auto-resizing to fit error messages
    - Customizable callbacks for completion and error handling
    """

    def __init__(self, parent=None, title="Processing", tasks=None):
        """
        Initialize the threaded loading dialog

        Args:
            parent: Parent widget
            title: Dialog window title
            tasks: List of task dictionaries (see TaskWorkerThread for format)
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumSize(450, 180)
        self.setMaximumWidth(600)
        self.parent_widget = parent

        self.tasks = tasks or []
        self.worker_thread = None
        self.on_complete_callback = None
        self.on_error_callback = None
        self.auto_close_on_complete = True
        self.auto_close_delay = 800  # milliseconds

        self._setup_ui()
        self.resize(450, 180)
        self._center_on_parent()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        self.status_label.setMinimumHeight(40)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # indeterminate by default
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # Info label
        self.info_label = QLabel("This may take a few moments...")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-size: 11px; color: #666;")
        layout.addWidget(self.info_label)

        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMaximumWidth(100)
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _center_on_parent(self):
        """Center the dialog on the parent widget"""
        if self.parent_widget:
            parent_rect = self.parent_widget.geometry()
            x = parent_rect.center().x() - self.width() // 2
            y = parent_rect.center().y() - self.height() // 2
            self.move(x, y)

    def _adjust_size_for_content(self):
        """Adjust dialog size to fit content"""
        self.adjustSize()
        # self._center_on_parent()

    def set_tasks(self, tasks):
        """
        Set the tasks to be executed

        Args:
            tasks: List of task dictionaries (see TaskWorkerThread for format)
        """
        self.tasks = tasks

    def set_on_complete_callback(self, callback):
        """
        Set a callback function to be called when all tasks complete

        Args:
            callback: Function that takes results as parameter
        """
        self.on_complete_callback = callback

    def set_on_error_callback(self, callback):
        """
        Set a callback function to be called when an error occurs

        Args:
            callback: Function that takes error_message as parameter
        """
        self.on_error_callback = callback

    def set_auto_close(self, enabled, delay=800):
        """
        Configure auto-close behavior on completion

        Args:
            enabled: Whether to auto-close on completion
            delay: Delay in milliseconds before closing
        """
        self.auto_close_on_complete = enabled
        self.auto_close_delay = delay

    def start(self):
        """Start executing the task queue"""
        if not self.tasks:
            self.set_error("No tasks to execute")
            return

        self.worker_thread = TaskWorkerThread(self.tasks)

        # Connect signals
        self.worker_thread.task_started.connect(self._on_task_started)
        self.worker_thread.task_completed.connect(self._on_task_completed)
        self.worker_thread.all_completed.connect(self._on_all_completed)
        self.worker_thread.error.connect(self._on_error)
        self.worker_thread.progress.connect(self._on_progress)
        self.worker_thread.finished.connect(self._on_thread_finished)

        self.worker_thread.start()

    def execute(self):
        """Start tasks and show the dialog (blocking)"""
        self.start()
        return self.exec()

    def _on_task_started(self, task_index, description):
        """Handle task started event"""
        self.status_label.setText(description)
        self._adjust_size_for_content()

    def _on_task_completed(self, task_index):
        """Handle task completed event"""
        pass

    def _on_progress(self, current, total):
        """Handle progress update"""
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
            self.progress_bar.setTextVisible(True)
            self.progress_bar.setFormat(f"{current}/{total}")
            # Center the text
            self.progress_bar.setAlignment(Qt.AlignCenter)

    def _on_all_completed(self, results):
        """Handle all tasks completed"""
        self.set_complete()

        if self.on_complete_callback:
            self.on_complete_callback(results)

        if self.auto_close_on_complete:
            QTimer.singleShot(self.auto_close_delay, self.accept)

    def _on_error(self, error_message):
        """Handle error"""
        self.set_error(error_message)

        if self.on_error_callback:
            self.on_error_callback(error_message)

        # Auto-close after showing error
        QTimer.singleShot(5000, self.reject)

    def _on_thread_finished(self):
        """Handle thread finished (cleanup)"""
        if self.worker_thread:
            self.worker_thread.deleteLater()
            self.worker_thread = None

    def _on_cancel(self):
        """Handle cancel button click"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.worker_thread.quit()
            self.worker_thread.wait()

        self.reject()

    def set_status(self, text):
        """Update the status label"""
        self.status_label.setText(text)
        self._adjust_size_for_content()

    def set_error(self, error_message=None):
        """Display error state"""
        if error_message:
            self.status_label.setText(error_message)

        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #222;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #f44336;
                border-radius: 2px;
            }
        """)
        self.info_label.setText("")
        self.cancel_button.setText("Close")
        self._adjust_size_for_content()

    def set_complete(self):
        """Display completion state"""
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #222;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)
        self.status_label.setText("Processing complete!")
        self.info_label.setText("Success!")
        self.cancel_button.setText("Close")
        self._adjust_size_for_content()
