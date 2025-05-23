import cv2
import os


def lireVideo(video_path):
    max = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = max.read()
        if not ret:
            break
        frames.append(frame)
    return frames


def sauvegarderVideo(output_Video_Frames, output_Chemin_Video, output_Nom_Video):
    # Vérifie que le répertoire de sortie existe
    os.makedirs(output_Chemin_Video, exist_ok=True)

    # Construit le nom du fichier
    out_Chemin = os.path.join(output_Chemin_Video, f"{output_Nom_Video}.mp4")

    fourcc = int(cv2.VideoWriter.fourcc(*'mp4v'))
    hauteur, largeur = output_Video_Frames[0].shape[:2]
    out = cv2.VideoWriter(out_Chemin, fourcc, 24.0, (largeur, hauteur))

    for frame in output_Video_Frames:
        out.write(frame)
    out.release()
    print(f"Sauvegarder la vidéo dans {out_Chemin}")
