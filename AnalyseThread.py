from PyQt6.QtCore import QThread, pyqtSignal
from video_Foot_Ml.MainML import analyseYolo


class AnalyseThread(QThread):
    analyse_Terminee = pyqtSignal()  # Signal à émettre quand c’est terminé
    erreur = pyqtSignal()
    progression = pyqtSignal(int)

    def __init__(self, chemin_Video, video_Deja_Faite):
        super().__init__()
        self.chemin_Video = chemin_Video
        self.video_Deja_Faite = video_Deja_Faite

    def run(self):
        try:
            print("Lancement de l’analyse dans le thread…")

            def rappelProgression(pourcentage):
                self.progression.emit(pourcentage)

            analyseYolo(self.chemin_Video, self.video_Deja_Faite, rappel_Progression=rappelProgression)
            print("Analyse terminée dans le thread!")
            self.analyse_Terminee.emit()
        except Exception as e:
            print("Erreur dans le thread d’analyse :", e)
            self.erreur.emit()
