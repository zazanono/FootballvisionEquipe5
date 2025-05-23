from PyQt6.QtCore import QThread, pyqtSignal

from VideoFootMl.MainML import analyseYolo


# Classe AnalyseThread :
# Permet d’exécuter l’analyse vidéo dans un thread séparé pour ne pas bloquer l’interface graphique
class AnalyseThread(QThread):
    # Signal émis lorsque l’analyse est terminée
    analyse_Terminee = pyqtSignal()

    # Signal émis s’il y a une erreur pendant l’analyse
    erreur = pyqtSignal()

    # Signal émis pour suivre la progression (%)
    progression = pyqtSignal(int)

    def __init__(self, chemin_vid, vid_deja_faite):
        """
                Initialise le thread avec les paramètres nécessaires pour l’analyse.

                Paramètres :
                    chemin_vid : str
                        Chemin de la vidéo à analyser
                    vid_deja_faite : bool
                        True si les détections sont déjà en cache (track_stubs.pkl)
                """
        super().__init__()
        self.chemin_Video = chemin_vid
        self.video_Deja_Faite = vid_deja_faite

    def run(self):
        """
                Méthode appelée automatiquement quand le thread démarre.
                Elle exécute l’analyse et émet les signaux selon le déroulement.
                """
        try:
            print("Lancement de l’analyse dans le thread…")

            # Fonction de rappel utilisée pour transmettre la progression à l’interface
            def rappel_Progression(pourcentage):
                self.progression.emit(pourcentage)

            # Lance l’analyse complète en passant la fonction de progression
            analyseYolo(self.chemin_Video, self.video_Deja_Faite, progression_callback=rappel_Progression)
            print("Analyse terminée dans le thread !")
            self.analyse_Terminee.emit()  # Signale que tout s’est bien passé
        except Exception as e:
            print("Erreur dans le thread d’analyse :", e)
            self.erreur.emit()  # Signale une erreur à l’interface
