from typing import Optional

import typer
from rich.console import Console
from rich.rule import Rule

import util.nfcutil as nfcutil
import util.qrutil as qrutil

app = typer.Typer(add_completion=False)


@app.command(help="カメラでQRコードをスキャンしてそのURIをNFCタグに書き込む")
def scanwrite(
    uri_pattern: Optional[str] = typer.Option(
        default=None, help="検出されたURIがマッチすべき正規表現パターン"
    ),
    skip_test_after_write: bool = typer.Option(
        default=False, help="書き込み後のテストをスキップする"
    ),
):
    console = Console()

    with qrutil.get_handler() as qr_handler, nfcutil.get_handler() as nfc_handler:
        while True:
            with console.status(
                "[bold cyan] カメラにQRコードをかざしてください...", spinner="line"
            ):
                try:
                    visitor_connpass_uri = qr_handler.try_detect_with_camera(
                        pattern=uri_pattern
                    )
                except qrutil.StopDetection:
                    console.print(":black_square_for_stop: 処理の中止が要求されました")
                    return  # quit command
                else:
                    console.print(
                        f":white_check_mark: URIを検出しました: {visitor_connpass_uri}"
                    )

            with console.status(
                "[bold cyan] URIを書き込みます。NFCタグをタッチしてください...",
                spinner="line",
            ):
                try:
                    nfc_handler.write_uri(uri=visitor_connpass_uri)
                except nfcutil.NDEFError:
                    console.print(
                        ":x: [bold red] このNFCタグにはURIレコードを書き込むことが出来ません。QRコードのスキャンに戻ります..."
                    )
                    continue
                else:
                    console.print(":white_check_mark: URIの書き込みが完了しました")

            if not skip_test_after_write:
                with console.status(
                    "[bold cyan] URIが正常に書き込まれたかチェックします。NFCタグをタッチしてください...",
                    spinner_style="bold cyan",
                ):
                    if nfc_handler.test_uri(uri=visitor_connpass_uri):
                        console.print(
                            ":white_check_mark: URIが正常に書き込まれていることを確認しました"
                        )
                    else:
                        console.print(
                            ":x: [bold red] このNFCタグには正しいURIレコードが書き込まれていません。QRコードのスキャンに戻ります..."
                        )
                        continue

            console.print(Rule(f"URI: {visitor_connpass_uri} の書き込みが完了しました"))


@app.command(help="NFCタグに含まれるすべてのレコードを取得して表示する")
def showrecords():
    console = Console()

    with nfcutil.get_handler() as nfchandler:
        with console.status(
            "[bold cyan] NFCタグをタッチしてください...", spinner="line"
        ):
            try:
                records = nfchandler.get_records()
            except nfcutil.NDEFError:
                console.print(
                    ":x: [bold red] このNFCタグにはNFC Data Exchange Format (NDEF)形式のレコードがありません"
                )
            else:
                console.print(":card_file_box: 検出されたレコードのリスト", records)


if __name__ == "__main__":
    app()
