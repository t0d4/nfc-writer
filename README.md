# NFC reader/writer utility with rich output, powered by nfcpy

## これは何？

PyCon JP 2024の準備で使用するために作成したNFCリーダライタユーティリティです。
カメラでQRコードを読み取り、そのQRコードをデコードして得られるURIをNFCタグに書き込むことが出来ます。

![demo gif](https://github.com/user-attachments/assets/48ca0ad1-7b2a-48e1-aaf8-cf6779f9d5e4)

NFCリーダライタとしてSONYの[RC-S380](https://www.sony.co.jp/Products/felica/consumer/products/RC-S380.html)を使って動作確認済みです。

## 準備

> [!WARNING]
> Mac/Linux環境の場合はlibusbが標準でインストールされていますが、バージョンが1.0.0以上であることを確認してください。

1. [nfcpyのサポートするデバイスの一覧](https://nfcpy.readthedocs.io/en/latest/overview.html#supported-devices)に記載されたデバイスを準備してください。
2. Pythonプロジェクトマネージャーのuvを[Installation Guide](https://github.com/astral-sh/uv?tab=readme-ov-file#installation)に従ってインストールしてください。
3. 【Windows環境のみ】[nfcpyの公式ドキュメント](https://nfcpy.readthedocs.io/en/latest/topics/get-started.html)に従ってWinUSBとlibusbをインストールしてください。
4. 最後に、以下に従ってこのリポジトリをcloneし、仮想環境を作成してください。
    ```bash
    git clone https://github.com/t0d4/nfc-writer.git
    cd nfc-writer
    uv python install 3.11
    uv sync
    ```
5. `uv run python -m nfc` を実行してNFCリーダライタが使用可能かチェックしてください。エラーが出た場合はそのメッセージに従って使用可能な状態にしてください。


## 使い方

### 構文

```bash
uv run main.py COMMAND
```

```bash
user@host ~/Works/nfc-writer $ uv run main.py --help

 Usage: main.py [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────╮
│ scanwrite     カメラでQRコードをスキャンしてそのURIをNFCタグに書き込む   │
│ showrecords   NFCタグに含まれるすべてのレコードを取得して表示する        │
╰──────────────────────────────────────────────────────────────────╯
```


各コマンドの詳細については `uv run main.py COMMAND --help` で確認してください。

### Examples

- カメラを使って正規表現パターン `https://connpass.com/user/.+` にマッチするURIを持つQRコードを検出し、そのURIをNFCタグに書き込む
    ```bash
    uv run main.py scanwrite --uri-pattern "https://connpass.com/user/.+"
    ```
- カメラを使ってQRコードを検出し、それが持つURIをNFCタグに書き込む。書き込み後のチェックをスキップする。
    ```bash
    uv run main.py scanwrite --skip-test-after-write
    ```
- NFCタグの中に含まれているNDEFレコードの一覧を表示する
    ```bash
    uv run main.py showrecords
    ```