import os
import subprocess
import sys
from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import QApplication

def log_info(message):
    print(f"[{QtCore.QCoreApplication.applicationName()}][INFO]: {message}")

def log_error(message):
    print(f"[{QtCore.QCoreApplication.applicationName()}][ERROR]: {message}", file=sys.stderr)

def log_debug(message):
    app = QApplication.instance()
    if app and app.property("debug"):
        print(f"[{QtCore.QCoreApplication.applicationName()}][DEBUG]: {message}")

def log_warning(message):
    print(f"[{QtCore.QCoreApplication.applicationName()}][WARNING]: {message}")

def resourcePath(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return relative_path

def get_app_settings():
    return QtCore.QSettings("rischio", QtCore.QCoreApplication.applicationName())

def reset_settings():
    settings = get_app_settings()
    settings.clear()

def get_setting(key, default=None):
    settings = get_app_settings()
    if key in settings.allKeys():
        return settings.value(key)
    log_error(f"Setting {key} not found in settings, returning default value")
    return default

def runCommand(command, detach=False):
    if detach:
        # Start process in detached mode
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,  # Ignore output
            stderr=subprocess.DEVNULL
        )
        return process.pid  # Return the process ID of the detached process
    else:
        # Normal execution (waits for completion)
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        cmd_output, cmd_err = process.communicate()
        code = process.returncode
        return (cmd_output.decode("utf-8").strip(), cmd_err.decode("utf-8").strip(), code)


def set_dark_palette(app):
    """Apply a Dark Fusion Theme"""
    dark_palette = QtGui.QPalette()
    # Base Colors
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.black)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    # Disabled Colors
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtCore.Qt.darkGray)
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtCore.Qt.darkGray)
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtCore.Qt.darkGray)
    app.setPalette(dark_palette)