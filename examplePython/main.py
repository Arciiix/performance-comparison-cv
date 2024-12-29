import threading
from time import sleep
import cv2


def loop(stream_url: str, id: str, withFaceDetection: bool):
    print("Hello")

    if withFaceDetection:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore
        )

    cap = cv2.VideoCapture(stream_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)
    print("Start")

    while True:
        ret, frame = cap.read()

        if not ret:
            sleep(1)
            continue

        width, height = frame.shape[:2]

        if withFaceDetection:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (640, 480))
            gray = cv2.equalizeHist(gray)

            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30)
            )

            for x, y, w, h in faces:
                cv2.rectangle(
                    frame,
                    (x * width // 640, y * height // 480),
                    ((x + w) * width // 640, (y + h) * height // 480),
                    (0, 255, 0),
                    2,
                )

        cv2.imshow(f"Stream {id}", frame)

        if cv2.waitKey(1) == 27:
            break

        sys.stdout.write(id)
        sys.stdout.flush()
    cap.release()
    print("End")


def main(args):
    print("Hello main")

    if len(args) < 2:
        print("Usage: python main.py <stream_url>")
        return

    stream_url = args[1]

    t1 = threading.Thread(target=loop, args=(stream_url, ".", True))
    t2 = threading.Thread(target=loop, args=(stream_url, ",", False))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    cv2.destroyAllWindows()
    cv2.waitKey(1)


if __name__ == "__main__":
    import sys

    main(sys.argv)
