from PyQt6.QtCore import QThread, pyqtSignal
from video_foot_ml.MainML import analyseYolo

class AnalyseThread(QThread):
    analyse_terminee = pyqtSignal()  # Signal à émettre quand c’est terminé
    erreur = pyqtSignal()
    progression = pyqtSignal(int)

    def __init__(self, chemin_vid, vid_deja_faite):
        super().__init__()
        self.chemin_vid = chemin_vid
        self.vid_deja_faite = vid_deja_faite

    def run(self):
        try:
            print("Lancement de l’analyse dans le thread…")

            def callback_progression(pourcentage):
                self.progression.emit(pourcentage)

            analyseYolo(self.chemin_vid, self.vid_deja_faite, progression_callback=callback_progression)
            print("Analyse terminée dans le thread !")
            self.analyse_terminee.emit()
        except Exception as e:
            print("Erreur dans le thread d’analyse :", e)
            self.erreur.emit()