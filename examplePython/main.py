from math import floor
import os
import queue
import threading
from time import sleep
import cv2


class VideoCapture:
    def __init__(self, name):
        self.cap = cv2.VideoCapture(name)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()  # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.q.put(frame)

    def release(self):
        self.cap.release()

    def read(self):
        return self.q.get()


def loop(stream_url: str, id: str, withFaceDetection: bool):
    print("Hello")

    if withFaceDetection:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore
        )

    cap = VideoCapture(stream_url)
    print("Start")

    while True:
        frame = cap.read()

        if frame is None:
            print("Error: Empty Frame")
            continue

        height, width = frame.shape[:2]

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
                    (floor(x * width / 640), floor(y * height / 480)),
                    (floor((x + w) * width / 640), floor((y + h) * height / 480)),
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
    os._exit(0)


def main(args):
    print("Hello main")

    if len(args) < 2:
        print("Usage: python main.py <stream_url>")
        return

    stream_url = args[1]

    t1 = threading.Thread(target=loop, args=(stream_url, ".", True))
    t2 = threading.Thread(target=loop, args=(stream_url, ",", False))
    t3 = threading.Thread(target=loop, args=(stream_url, "a", True))
    t4 = threading.Thread(target=loop, args=(stream_url, "b", False))
    t5 = threading.Thread(target=loop, args=(stream_url, "c", False))
    t6 = threading.Thread(target=loop, args=(stream_url, "d", False))
    t7 = threading.Thread(target=loop, args=(stream_url, "e", False))
    t8 = threading.Thread(target=loop, args=(stream_url, "f", True))

    threads = [t1, t2, t3, t4, t5, t6, t7, t8]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    cv2.destroyAllWindows()
    cv2.waitKey(1)


if __name__ == "__main__":
    import sys

    main(sys.argv)
