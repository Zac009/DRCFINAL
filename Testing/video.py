import cv2

def main():
    cap = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Setup video writer
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

    print("Camera opened. Press 'q' to quit, 'r' to start/stop recording.")
    recording = False

    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, -1)
        if not ret:
            print("Error: Failed to grab frame.")
            break

        if recording:
            out.write(frame)

        # Overlay info
        cv2.putText(frame, f"Res: {w}x{h}  FPS: {fps:.0f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, "REC" if recording else "STANDBY", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255) if recording else (128, 128, 128), 2)

        cv2.imshow("Camera - press r to record, q to quit", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Quitting.")
            break
        elif key == ord('r'):
            recording = not recording
            print("Recording..." if recording else "Stopped recording.")

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()