from ultralytics import YOLO

# model = YOLO('models/yolov8l')
model = YOLO('models/bestf1.pt')

resultats = model.predict('input_videos/foot2.mov', save=True)
print(resultats[0])
print('========================================')
for box in resultats[0].boxes:
    print(box)
