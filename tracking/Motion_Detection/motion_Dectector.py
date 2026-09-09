from ultralytics import YOLO
import cv2

model = YOLO("yolov8s.pt")
model.to("cuda")

cap = cv2.VideoCapture(0)

track_hist = {}

while True:
    ret, frame = cap.read()

    if not ret:
        break

    results = model.track(frame, persist=True)

    for result in results:
        boxes = result.boxes

        for box in boxes:
            if box.id is None:
                continue
            
            track_id = int(box.id[0])
            
            cls = int(box.cls[0])

            if cls != 0:
                continue

            x, y, w, h = map(int, box.xyxy[0])

            cx = (x + w) // 2
            cy = (y + h) // 2

            if track_id not in track_hist:
                track_hist[track_id] = []
            
            track_hist[track_id].append((cx, cy))

            if len(track_hist[track_id]) > 30:
                track_hist[track_id].pop(0)
            
            for i in range(1, len(track_hist[track_id])):
                cv2.line(frame, track_hist[track_id][i-1], track_hist[track_id][i], (255, 0, 0), 3)

            conf = float(box.conf[0])

            cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)
            cv2.putText(frame, f"ID : {track_id}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 123), 2)
    
    cv2.imshow("YOLO Person Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()