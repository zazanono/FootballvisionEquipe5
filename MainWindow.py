import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QApplication

from Interfaces.Application import Application
from Interfaces.Chargement import Chargement
from Interfaces.Menu import Menu


# Classe MainWindow : fenêtre principale de l’application "Vision FC"
# Elle gère les différents écrans via un QStackedWidget
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Titre et style de la fenêtre principale
        self.setWindowTitle("Vision FC")
        self.showMaximized()
        self.setStyleSheet("background-color: #222F49")  # Couleur de fond

        # Widget empilé qui contiendra tous les écrans (menu, chargement, application)
        self.stacked_widget = QStackedWidget()

        # Icône de la fenêtre (logo du projet)
        self.setWindowIcon(QIcon("images/logo.png"))

        # Création des différents écrans de l’application
        self.ecran_App = Application(self.stacked_widget)  # Écran principal d’analyse (vidéo, etc.)
        self.chargement_Ecran = Chargement(self.stacked_widget, self.ecran_App)  # Écran de chargement
        self.menu = Menu(self.stacked_widget, self.chargement_Ecran)  # Écran du menu d’accueil

        # Ajout des écrans au QStackedWidget dans un ordre précis
        self.stacked_widget.addWidget(self.menu)  # Index 0 : menu principal
        self.stacked_widget.addWidget(self.chargement_Ecran)  # Index 1 : chargement
        self.stacked_widget.addWidget(self.ecran_App)  # Index 2 : application (analyse)

        # Mise en page de l’ensemble
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)


# Point d’entrée du programme
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
