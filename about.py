import sys
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication, QSizePolicy
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QCoreApplication
from . import core

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.resize(300, 200)
        self.setFixedSize(300, 200)
        self.app_name = QCoreApplication.applicationName()
        self.app_version = QCoreApplication.applicationVersion()

        # Create a vertical layout
        layout = QVBoxLayout(self)

        # Company Name
        company_label = QLabel(f"<h2>{self.app_name}</h2>")
        company_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(company_label)

        # Display the icon in the dialog
        # The icon will be in this module's resources
        icon_pixmap = QPixmap(core.resourcePath('RischioPysideWidgets/images/rischio.png'))
        if not icon_pixmap.isNull():
            icon_label = QLabel()
            icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)

        # App Version
        version_label = QLabel("Version:" + QCoreApplication.applicationVersion())
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        # Links (clickable)
        website_link = QLabel('<a href="https://rischio.studio">Visit our Website</a>')
        website_link.setAlignment(Qt.AlignCenter)
        website_link.setOpenExternalLinks(True)
        layout.addWidget(website_link)

        copyright_label = QLabel("© 2025 Studio Rischio LLC")
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Shrink when needed

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = AboutDialog()
    dialog.exec()
