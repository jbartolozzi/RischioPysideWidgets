import sys
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QVBoxLayout, QWidget, QDialog, QLabel,
                             QProgressBar, QHBoxLayout)
from PySide6.QtCore import (Qt, QThread, Signal, QTimer,
                           QPropertyAnimation, QRect, QEasingCurve)
from PySide6.QtGui import QMovie, QPainter, QColor, QFont, QPalette


class Worker(QThread):
    """Worker thread for running background operations"""
    finished = Signal()
    progress = Signal(int)
    error = Signal(str)
    result = Signal(object)

    def __init__(self, operation, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            # Run the operation
            result = self.operation(*self.args, **self.kwargs)
            self.result.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class LoadingDialog(QDialog):
    """Custom loading dialog with animation - Dark Theme"""

    def __init__(self, parent=None, message="Loading..."):
        super().__init__(parent)
        self.setWindowTitle("Processing")
        self.setModal(True)
        self.setFixedSize(300, 150)

        # Remove window frame for cleaner look
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        # Setup UI
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Message label
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        self.message_label.setFont(font)

        # Create spinning dots animation
        self.dots_label = QLabel("...")
        self.dots_label.setAlignment(Qt.AlignCenter)

        # Progress bar (indeterminate)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setTextVisible(False)

        # Add widgets to layout
        layout.addWidget(self.message_label)
        layout.addWidget(self.dots_label)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        # Setup animation timer for dots
        self.dots_timer = QTimer()
        self.dots_timer.timeout.connect(self.animate_dots)
        self.dots_count = 0
        self.dots_timer.start(500)  # Update every 500ms

    def animate_dots(self):
        """Animate the dots to show processing"""
        dots = ["", ".", "..", "...", "..", "."]
        self.dots_label.setText(dots[self.dots_count % len(dots)])
        self.dots_count += 1

    def set_message(self, message):
        """Update the loading message"""
        self.message_label.setText(message)

    def closeEvent(self, event):
        """Stop timers when closing"""
        self.dots_timer.stop()
        super().closeEvent(event)


class SpinnerDialog(QDialog):
    """Alternative loading dialog with custom spinner animation - Dark Theme"""

    def __init__(self, parent=None, message="Processing..."):
        super().__init__(parent)
        self.setWindowTitle("Loading")
        self.setModal(True)
        self.setFixedSize(250, 250)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        self.angle = 0
        self.message = message

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)  # Update every 50ms

        # Dark theme style
        self.setStyleSheet("""
            QDialog {
                background-color: #353535;
                border: 2px solid #5a5a5a;
                border-radius: 15px;
            }
        """)

    def paintEvent(self, event):
        """Custom paint event for spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw dark background
        painter.fillRect(self.rect(), QColor(53, 53, 53))

        # Draw spinner with blue accent color
        painter.translate(self.width() / 2, self.height() / 2 - 20)
        painter.rotate(self.angle)

        for i in range(12):
            color = QColor(74, 144, 226)  # Blue accent color
            color.setAlphaF(1.0 - (i / 12.0))
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(-4, -30, 8, 15)
            painter.rotate(30)

        painter.resetTransform()

        # Draw message in white
        painter.setPen(QColor(255, 255, 255))
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(0, 60, 0, 0),
                        Qt.AlignCenter, self.message)

    def rotate(self):
        """Rotate the spinner"""
        self.angle = (self.angle + 10) % 360
        self.update()

    def set_message(self, message):
        """Update the message"""
        self.message = message
        self.update()

    def closeEvent(self, event):
        """Stop timer when closing"""
        self.timer.stop()
        super().closeEvent(event)


class MainWindow(QMainWindow):
    """Main application window with examples - Dark Theme"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading Popup Examples - Dark Theme")
        self.setGeometry(100, 100, 400, 300)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Layout
        layout = QVBoxLayout()

        # Example buttons
        btn1 = QPushButton("Run Operation with Progress Bar Loading")
        btn1.clicked.connect(self.run_with_progress_loading)

        btn2 = QPushButton("Run Operation with Spinner Loading")
        btn2.clicked.connect(self.run_with_spinner_loading)

        btn3 = QPushButton("Run Quick Operation (2 seconds)")
        btn3.clicked.connect(self.run_quick_operation)

        btn4 = QPushButton("Run Operation with Error")
        btn4.clicked.connect(self.run_with_error)

        self.result_label = QLabel("Results will appear here...")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #191919;
                border: 1px solid #5a5a5a;
                border-radius: 5px;
                color: #ffffff;
            }
        """)

        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)
        layout.addWidget(btn4)
        layout.addWidget(self.result_label)
        layout.addStretch()

        central.setLayout(layout)

        # Dark theme button styles
        self.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 12px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #6ab0ff;
            }
            QPushButton:pressed {
                background-color: #357abd;
            }
            QMainWindow {
                background-color: #353535;
            }
        """)

    def long_running_operation(self):
        """Simulates a long-running operation"""
        time.sleep(5)  # Simulate work
        return "Operation completed successfully! Result: 42"

    def quick_operation(self):
        """Simulates a quick operation"""
        time.sleep(2)
        return "Quick operation done!"

    def error_operation(self):
        """Simulates an operation that raises an error"""
        time.sleep(1)
        raise ValueError("Something went wrong in the operation!")

    def run_with_progress_loading(self):
        """Run operation with progress bar loading dialog"""
        # Create and show loading dialog
        self.loading_dialog = LoadingDialog(self, "Processing data...")

        # Create worker thread
        self.worker = Worker(self.long_running_operation)
        self.worker.finished.connect(self.loading_dialog.close)
        self.worker.result.connect(self.on_operation_complete)
        self.worker.error.connect(self.on_operation_error)

        # Start operation
        self.worker.start()
        self.loading_dialog.exec()

    def run_with_spinner_loading(self):
        """Run operation with spinner loading dialog"""
        # Create and show spinner dialog
        self.spinner_dialog = SpinnerDialog(self, "Working on it...")

        # Create worker thread
        self.worker = Worker(self.long_running_operation)
        self.worker.finished.connect(self.spinner_dialog.close)
        self.worker.result.connect(self.on_operation_complete)
        self.worker.error.connect(self.on_operation_error)

        # Start operation
        self.worker.start()
        self.spinner_dialog.exec()

    def run_quick_operation(self):
        """Run a quick operation"""
        self.loading_dialog = LoadingDialog(self, "Quick processing...")

        self.worker = Worker(self.quick_operation)
        self.worker.finished.connect(self.loading_dialog.close)
        self.worker.result.connect(self.on_operation_complete)
        self.worker.error.connect(self.on_operation_error)

        self.worker.start()
        self.loading_dialog.exec()

    def run_with_error(self):
        """Run operation that will error"""
        self.loading_dialog = LoadingDialog(self, "Attempting operation...")

        self.worker = Worker(self.error_operation)
        self.worker.finished.connect(self.loading_dialog.close)
        self.worker.result.connect(self.on_operation_complete)
        self.worker.error.connect(self.on_operation_error)

        self.worker.start()
        self.loading_dialog.exec()

    def on_operation_complete(self, result):
        """Handle successful operation completion"""
        self.result_label.setText(f"Success: {result}")
        self.result_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #1a3d1a;
                border: 1px solid #2d5a2d;
                border-radius: 5px;
                color: #90ee90;
            }
        """)

    def on_operation_error(self, error):
        """Handle operation error"""
        self.result_label.setText(f"Error: {error}")
        self.result_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #3d1a1a;
                border: 1px solid #5a2d2d;
                border-radius: 5px;
                color: #ff6b6b;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())