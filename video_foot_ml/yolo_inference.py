from ultralytics import YOLO

# model = YOLO('models/yolov8l')
model = YOLO('models/bestf1.pt')

results = model.predict('input_videos/foot2.mov', save=True)
print(results[0])
print('========================================')
for box in results[0].boxes:
    print(box)
