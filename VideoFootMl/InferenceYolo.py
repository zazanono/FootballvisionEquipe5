from ultralytics import YOLO

# Chargement du modèle YOLOv8
# model = YOLO('Models/yolov8l') (pré-entraîné)
model = YOLO('Models/bestf1.pt')  # Modèle personnalisé entraîné (checkpoint)

# Prédiction sur une vidéo donnée
# Le paramètre save=True permet de sauvegarder automatiquement la vidéo annotée
resultats = model.predict('VideosInput/foot2.mov', save=True)

# Affiche les résultats de la première frame (résumé)
print(resultats[0])
print('========================================')

# Parcours des boîtes englobantes détectées dans la première frame
for box in resultats[0].boxes:
    print(box)
