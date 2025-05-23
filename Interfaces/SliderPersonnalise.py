import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSlider


class SliderPersonnalise(QSlider):

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            mouse_x = event.position().x()  # Position X du clic local
            slider_width = self.width()  # Largeur totale du slider

            # Calcul de la position en pourcentage
            position = max(0, min(100, (mouse_x / slider_width) * 100))

            # Déplacement de la vidéo au frame correspondant
            if hasattr(self.parent(), 'cap') and self.parent().cap:
                total_Frames = self.parent().cap.get(cv2.CAP_PROP_FRAME_COUNT)
                nouvelle_Frame = int(total_Frames * (position / 100))
                self.parent().cap.set(cv2.CAP_PROP_POS_FRAMES, nouvelle_Frame)

                # Mise à jour instantanée
                self.parent().update_frame()

            # Déplacement du curseur du slider
            self.setValue(int(position))

            # Appel de l'événement parent (pour éviter des bugs)
            super().mousePressEvent(event)
