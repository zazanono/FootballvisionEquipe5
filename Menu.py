import sys

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QStackedWidget, QFileDialog, QLabel
from PyQt6.QtCore import Qt


class Menu(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget  # Garde une référence au QStackedWidget

        self.setStyleSheet("background-color: #222F49")  # Changer la couleur

        layout = QVBoxLayout()
        button = QPushButton("Aller à l'application")
        button.setStyleSheet("color: white; font-size: 20px;")
        button.clicked.connect(self.go_to_app)
        layout.addWidget(button)

        self.setLayout(layout)

        # Label pour afficher le chemin du fichier sélectionné
        self.label = QLabel("Aucun fichier sélectionné")
        self.label.setStyleSheet("color: white; font-size: 20px;")
        layout.addWidget(self.label)


        # Bouton pour ouvrir le sélecteur de fichier
        self.buttonParcourir = QPushButton("Parcourir...")
        self.buttonParcourir.setStyleSheet("color: white; font-size: 20px;")
        self.buttonParcourir.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.buttonParcourir)

        self.setLayout(layout)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier", "","Video(*.mp4)")

        if file_path:  # Vérifie si l'utilisateur a sélectionné un fichier
            self.label.setText(file_path)  # Affiche le chemin du fichier sélectionné

    def go_to_app(self):
        self.stacked_widget.setCurrentIndex(1)  # Change d'affichage

class Application(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()
        buttonMenu = QPushButton("Retour au menu")
        buttonMenu.clicked.connect(self.go_to_menu)
        buttonMenu.setStyleSheet("color: white; font-size: 15px;")
        layout.addWidget(buttonMenu, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(buttonMenu)
        self.setLayout(layout)

    def go_to_menu(self):
        self.stacked_widget.setCurrentIndex(0)  # Retour à l'accueil


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basketvision")
        self.showMaximized()

        self.stacked_widget = QStackedWidget()

        self.setStyleSheet("background-color: #1A2438")  # Changer la couleur

        self.menu = Menu(self.stacked_widget)
        self.application = Application(self.stacked_widget)

        self.stacked_widget.addWidget(self.menu)  # Index 0 : Menu
        self.stacked_widget.addWidget(self.application)  # Index 1 : Application

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())