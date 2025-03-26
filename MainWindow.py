import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QApplication

from Interfaces.InterfaceApplication import Application
from Interfaces.InterfaceMenu import Menu


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vision FC")
        self.showMaximized()
        self.setStyleSheet("background-color: #222F49")  # Changer la couleur

        self.stacked_widget = QStackedWidget()
        self.setWindowIcon(QIcon("images/logo.png"))
        self.app_screen = Application(self.stacked_widget)  # Crée l'écran de l'application
        self.menu = Menu(self.stacked_widget, self.app_screen)  # Passe une référence à l'application

        self.stacked_widget.addWidget(self.menu)  # Index 0 : Menu
        self.stacked_widget.addWidget(self.app_screen)  # Index 1 : Application

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())