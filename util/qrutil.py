import re
from contextlib import contextmanager
from typing import Any, Generator, Optional

import cv2


class StopDetection(Exception):
    pass


class QRHandler:
    def __init__(self, cam_index: int) -> None:
        """:warning: This class is not intended to be instantiated directly.

        Args:
            cam_index (int): index of camera to use.
        """
        self.vcap = cv2.VideoCapture(cam_index)
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
            cv2.destroyWindow(self.window_name)


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
