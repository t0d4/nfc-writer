import os
import re
import threading
from contextlib import contextmanager
from queue import Empty, Queue
from typing import Any, Generator, Optional

import cv2

os.environ["OPENCV_LOG_LEVEL"] = "OFF"  # suppress INFO logging


class StopDetection(Exception):
    pass


class ThreadedVideoCapture:
    def __init__(self, cam_index: int) -> None:
        self.vcap = cv2.VideoCapture(cam_index)
        self.frame_q = Queue()
        self.stop_signal_q = Queue()
        th = threading.Thread(target=self._reader, daemon=True)
        th.start()

    def _reader(self):
        while True:
            if not self.stop_signal_q.empty():  # when cancellation is requested
                return

            capture_ok, frame = self.vcap.read()
            if not capture_ok:
                break
            if not self.frame_q.empty():
                try:
                    _ = self.frame_q.get_nowait()  # discard unprocessed frame
                except Empty:
                    pass
            self.frame_q.put_nowait(frame)

    def read(self):
        return True, self.frame_q.get()

    def release(self):
        self.stop_signal_q.put("cancel")
        self.vcap.release()


class QRHandler:
    def __init__(self, cam_index: int) -> None:
        """:warning: This class is not intended to be instantiated directly.

        Args:
            cam_index (int): index of camera to use.
        """
        self.vcap = ThreadedVideoCapture(cam_index)
        self.qcd = cv2.QRCodeDetectorAruco()
        self.window_name = "QR Code Detector (Press q to exit)"

    def close(self):
        self.vcap.release()

    def try_detect_with_camera(self, pattern: Optional[str] = None) -> str:
        """open camera and try to detect a QR code, then return the decoded string.

        Args:
            pattern (Optional[str]): a regex pattern that the decoded string should match. If provided, this method will not return until it reads a QR code whose decoded string matches the pattern.

        Raises:
            StopDetection: raised when user press "q" on the preview window

        Returns:
            str: string decoded from the QR code.
        """
        try:
            while True:
                capture_ok, frame = self.vcap.read()
                if capture_ok:
                    found_qr, decoded_strs, *_ = self.qcd.detectAndDecodeMulti(frame)
                    if found_qr:
                        for decoded_str in decoded_strs:
                            if not len(
                                decoded_str
                            ):  # sometimes empty strings could be detected
                                continue
                            if pattern and not re.fullmatch(
                                pattern=pattern, string=decoded_str
                            ):
                                continue
                            return decoded_str
                    cv2.imshow(self.window_name, frame)

                if cv2.waitKey(delay=1) & 0xFF == ord("q"):
                    raise StopDetection()
        finally:
            cv2.destroyAllWindows()


@contextmanager
def get_handler(cam_index: int = 0) -> Generator[QRHandler, Any, None]:
    """get handler for scanning QR code and decoding the value.

    Args:
        cam_index (int, optional): index of camera to use. Defaults to 0.

    Yields:
        Generator[QRHandler,Any,None]: handler for QR code operations.
    """
    qr_handler = None
    try:
        qr_handler = QRHandler(cam_index=cam_index)
        yield qr_handler
    finally:
        if qr_handler:
            qr_handler.close()
