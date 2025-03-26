import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSlider


class CustomSlider(QSlider):
    """ Barre de progression qui détecte le clic directement """

    def mousePressEvent(self, event):
        """ Gère le clic gauche sur le slider """
        if event.button() == Qt.MouseButton.LeftButton:
            mouse_x = event.position().x()  # Position X du clic local
            slider_width = self.width()  # Largeur totale du slider

            # Calcul de la position en pourcentage
            position = max(0, min(100, (mouse_x / slider_width) * 100))

            # Déplacement de la vidéo au frame correspondant
            if hasattr(self.parent(), 'cap') and self.parent().cap:
                total_frames = self.parent().cap.get(cv2.CAP_PROP_FRAME_COUNT)
                new_frame = int(total_frames * (position / 100))
                self.parent().cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

                # Mise à jour instantanée
                self.parent().update_frame()

            # Déplacement du curseur du slider
            self.setValue(int(position))

            # Appel de l'événement parent (pour éviter des bugs)
            super().mousePressEvent(event)

