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
        self.ecran_App = Application(self.stacked_widget)  # Crée l'écran de l'application
        self.chargement_Ecran = Chargement(self.stacked_widget, self.ecran_App)  # Crée l'écran de chargement
        self.menu = Menu(self.stacked_widget, self.chargement_Ecran)  # Crée l'écran du menu

        self.stacked_widget.addWidget(self.menu)  # Index 0 : Menu
        self.stacked_widget.addWidget(self.chargement_Ecran)  # Index 1 : Chargement
        self.stacked_widget.addWidget(self.ecran_App)  # Index 2 : Application

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
