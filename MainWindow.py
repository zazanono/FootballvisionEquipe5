import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QApplication

from Interfaces.Application import Application
from Interfaces.Menu import Menu
from Interfaces.Chargement import Chargement


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vision FC")
        self.showMaximized()
        self.setStyleSheet("background-color: #222F49")  # Changer la couleur

        self.stacked_widget = QStackedWidget()
        self.setWindowIcon(QIcon("images/logo.png"))
        self.app_ecran = Application(self.stacked_widget)  # Crée l'écran de l'application
        self.menu = Menu(self.stacked_widget, self.app_ecran)  # Crée l'écran du menu
        self.ecran_chargement = Chargement(self.stacked_widget)

        self.stacked_widget.addWidget(self.menu)  # Index 0 : Menu
        self.stacked_widget.addWidget(self.ecran_chargement)  # Index 1 : Chargement
        self.stacked_widget.addWidget(self.app_ecran)  # Index 2 : Application

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())