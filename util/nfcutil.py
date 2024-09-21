from contextlib import contextmanager
from typing import Any, Callable, Generator

from ndef import Record, UriRecord
from nfc import ContactlessFrontend
from nfc.tag import Tag


class NDEFError(Exception):
    pass


class NFCHandler:
    def __init__(self) -> None:
        """:warning: This class is not intended to be instantiated directly.

        Raises:
            IOError: raised when connection to reader/writer failed.
        """
        self.clf = ContactlessFrontend()
        if not self.clf.open("usb"):
            raise IOError("failed to open NFC reader/writer")

    def close(self):
        self.clf.close()

    # def _get_startup_fn(self) -> Callable[[Tag], Tag]:
    #     def startup_fn(tag: Tag):
    #         return tag

    #     return startup_fn

    # def _get_release_fn(self) -> Callable[[Tag], bool]:
    #     def release_fn(tag: Tag):
    #         return True

    #     return release_fn

    def _get_writer_fn(self, record: Record) -> Callable[[Tag], bool]:
        def writer_fn(tag: Tag):
            if not tag.ndef or not tag.ndef.is_writeable:
                raise NDEFError("NDEF was not found or NDEF is not writeable")

            # this substitution triggers the update
            tag.ndef.records = [record]

            # assert tag.ndef.has_changed  # TODO: check this
            return True

        return writer_fn

    def write_uri(self, uri: str):
        """write provided URI to NFC tag.

        Args:
            uri (str): URI as a string

        Raises:
            NDEFError: raised when NDEF was not found or NDEF is not writeable
        """
        uri_record = UriRecord(uri)
        self.clf.connect(rdwr={"on-connect": self._get_writer_fn(record=uri_record)})

    def test_uri(self, uri: str) -> bool:
        """test if NFC tag has the provided URI as a UriRecord.

        Args:
            uri (str): URI to check

        Returns:
            bool: True if UriRecord built from uri is contained in records of the NFC tag.
        """
        uri_record = UriRecord(uri)
        return uri_record in self.get_records()

    def get_records(self) -> list[Record]:
        """get all records in NFC tag.

        Raises:
            NDEFError: raised when data in NFC Data Exchange Format (NDEF) was not found

        Returns:
            list[Record]: records of the NFC tag.
        """
        # returning False from on-connect callback means it should return Tag as soon as NFC tag is detected.
        tag: Tag = self.clf.connect(rdwr={"on-connect": lambda _: False})
        if not tag.ndef:
            raise NDEFError("data in NFC Data Exchange Format (NDEF) was not found")
        return tag.ndef.records


@contextmanager
def get_handler() -> Generator[NFCHandler, Any, None]:
    """get handler for various NFC operations.

    Yields:
        Generator[NFCHandler,Any,None]: handler for NFC operations.
    """
    nfc_handler = None
    try:
        nfc_handler = NFCHandler()
        yield nfc_handler
    finally:
        if nfc_handler:
            nfc_handler.close()
