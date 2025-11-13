import sys
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication, QSizePolicy, QScrollArea, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QCoreApplication
from . import core

class AboutDialog(QDialog):
    def __init__(self, parent=None, open_source_projects=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.open_source_projects = open_source_projects or []

        # Calculate height based on whether we have projects
        base_height = 200
        if self.open_source_projects:
            # Add extra height for projects section
            base_height = min(500, 250 + len(self.open_source_projects) * 25)

        self.resize(400, base_height)
        self.setFixedSize(400, base_height)
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
        icon_pixmap = QPixmap(core.resourcePath('icons/rischio.png'))
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

        # Open Source Projects Section
        if self.open_source_projects:
            # Add separator
            layout.addSpacing(10)

            projects_header = QLabel("<h3>Third Party</h3>\n<p>This app relies on the following libraries:</p>")
            projects_header.setAlignment(Qt.AlignCenter)
            layout.addWidget(projects_header)

            # Create scroll area for projects
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setFrameShape(QScrollArea.NoFrame)

            # Container widget for projects
            projects_widget = QWidget()
            projects_layout = QVBoxLayout(projects_widget)
            projects_layout.setContentsMargins(5, 5, 5, 5)
            projects_layout.setSpacing(5)

            # Add each project as a clickable link
            for project in self.open_source_projects:
                if isinstance(project, dict):
                    name = project.get('name', 'Unknown')
                    url = project.get('url', '#')
                elif isinstance(project, tuple) and len(project) == 2:
                    name, url = project
                else:
                    continue  # Skip invalid entries

                project_link = QLabel(f'<a href="{url}">{name}</a>')
                project_link.setAlignment(Qt.AlignCenter)
                project_link.setOpenExternalLinks(True)
                projects_layout.addWidget(project_link)

            projects_layout.addStretch()
            scroll_area.setWidget(projects_widget)
            layout.addWidget(scroll_area)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Example with open source projects
    projects = [
        {'name': 'PySide6', 'url': 'https://wiki.qt.io/Qt_for_Python'},
        {'name': 'MediaPipe', 'url': 'https://google.github.io/mediapipe/'},
        {'name': 'NumPy', 'url': 'https://numpy.org/'},
        {'name': 'OpenCV', 'url': 'https://opencv.org/'},
        # You can also use tuples: ('Project Name', 'https://url.com')
    ]

    dialog = AboutDialog(open_source_projects=projects)
    dialog.exec()