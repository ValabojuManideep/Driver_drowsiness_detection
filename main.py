import cv2
import threading
import time
from playsound import playsound
from drowsiness_detector import DrowsinessDetector
from drive_uploader import upload_to_drive


EAR_THRESHOLD = 0.25
EAR_CONSEC_FRAMES = 20

def sound_alarm(path):
    playsound(path)

def main():
    detector = DrowsinessDetector("shape_predictor_68_face_landmarks.dat")
    cap = cv2.VideoCapture(0)

    # Read the first frame to get size
    ret, frame = cap.read()
    if not ret:
        print("Failed to read from webcam.")
        return

    height, width = frame.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (width, height))

    counter = 0
    alarm_on = False
    drowsiness_detected = False
    start_time = time.time()
    max_duration = 10 * 60  # 10 minutes

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame read failed.")
            break

        frame, ear = detector.detect(frame)
        out.write(frame)  # Record after processing

        if ear < EAR_THRESHOLD:
            counter += 1
            if counter >= EAR_CONSEC_FRAMES:
                if not alarm_on:
                    alarm_on = True
                    drowsiness_detected = True
                    threading.Thread(target=sound_alarm, args=("alert.wav",), daemon=True).start()
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            counter = 0
            alarm_on = False

        cv2.putText(frame, f"EAR: {ear:.2f}", (500, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("Stopped by user.")
            break
        if time.time() - start_time > max_duration:
            print("Recording stopped after 10 minutes.")
            break
    # if alarm_on:
    #     print("Drowsiness detected. Uploading video to Drive...")
    #     upload_to_drive("output.avi")
    # else:
    #     print("No drowsiness detected. Skipping upload.")

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Recording saved as output.avi")
    print("Recording saved as output.avi")

    if drowsiness_detected:
        print("Drowsiness was detected. Uploading to Google Drive...")
        upload_to_drive("output.avi")
    else:
        print("No drowsiness detected. Skipping upload.")


if __name__ == "__main__":
    main()
