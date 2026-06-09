import cv2

def main():
    cap = cv2.VideoCapture(0)  # 0 = default camera

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Camera opened. Press 'q' to quit, 's' to save a snapshot.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Overlay FPS info
        fps = cap.get(cv2.CAP_PROP_FPS)
        h, w = frame.shape[:2]
        cv2.putText(frame, f"Res: {w}x{h}  FPS: {fps:.0f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Camera Test - press q to quit", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Quitting.")
            break
        elif key == ord('s'):
            filename = "snapshot.jpg"
            cv2.imwrite(filename, frame)
            print(f"Snapshot saved to {filename}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()