import os

import cv2


def lireVideo(chemin_Video):
    """
        Lit une vidéo depuis un fichier et retourne toutes les frames sous forme de liste.

        Paramètre :
            chemin_Video : str
                Chemin complet vers le fichier vidéo à lire.

        Retour :
            frames : list[np.ndarray]
                Liste contenant chaque image (frame) de la vidéo.
        """
    cap = cv2.VideoCapture(chemin_Video)  # Ouvre la vidéo
    frames = []
    while True:
        ret, frame = cap.read()  # Lit une frame
        if not ret:  # Si plus de frames disponibles (ou erreur), on arrête
            break
        frames.append(frame)  # Ajoute la frame à la liste
    return frames


def sauvegarderVideo(output_Frames_Video, output_Chemin_Video, output_Nom_Video):
    """
        Sauvegarde une liste de frames comme une vidéo .mp4.

        Paramètres :
            output_Frames_Video : list[np.ndarray]
                Liste des images (frames) à écrire dans la vidéo.
            output_Chemin_Video : str
                Dossier de destination pour la vidéo.
            output_Nom_Video : str
                Nom du fichier vidéo de sortie (sans extension).

        Effet :
            Crée un fichier .mp4 contenant les frames au chemin spécifié.
        """
    # S’assure que le dossier de sortie existe
    os.makedirs(output_Chemin_Video, exist_ok=True)

    # Construit le chemin complet du fichier de sortie
    out_path = os.path.join(output_Chemin_Video, f"{output_Nom_Video}.mp4")

    # Définition du codec vidéo 'mp4v'
    fourcc = int(cv2.VideoWriter.fourcc(*'mp4v'))
    # Récupère la taille des frames à partir de la première image
    hauteur, largeur = output_Frames_Video[0].shape[:2]
    # Création de l'objet de sortie vidéo
    out = cv2.VideoWriter(out_path, fourcc, 24.0, (largeur, hauteur))

    # Écrit chaque frame dans la vidéo
    for frame in output_Frames_Video:
        out.write(frame)
    out.release()  # Libère les ressources
    print(f"Vidéo sauvegardée dans {out_path}")
