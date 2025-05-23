import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSlider


# Classe personnalisée pour la barre de progression vidéo
# Hérite de QSlider et permet de cliquer directement sur la barre pour déplacer la vidéo
class BarrePersonalisee(QSlider):

    def mousePressEvent(self, event):
        """ Méthode déclenchée lors d'un clic souris sur la barre de progression """
        if event.button() == Qt.MouseButton.LeftButton:
            souris_X = event.position().x()  # Position X du clic dans le widget
            largeur_Barre = self.width()  # Largeur totale de la barre (en pixels)

            # Convertit la position du clic en pourcentage (entre 0 et 100)
            position = max(0, min(100, (souris_X / largeur_Barre) * 100))

            # Vérifie si le parent contient un objet OpenCV valide
            if hasattr(self.parent(), 'cap') and self.parent().cap:
                total_Frames = self.parent().cap.get(cv2.CAP_PROP_FRAME_COUNT)
                nouvelle_Frame = int(total_Frames * (position / 100))
                # Déplace la lecture de la vidéo au frame correspondant
                self.parent().cap.set(cv2.CAP_PROP_POS_FRAMES, nouvelle_Frame)

                # Appelle une méthode de mise à jour visuelle si elle existe dans le parent
                self.parent().update_frame()

            # Déplace visuellement le curseur du slider
            self.setValue(int(position))

            # Appelle la version originale de l'événement (évite les bugs)
            super().mousePressEvent(event)
