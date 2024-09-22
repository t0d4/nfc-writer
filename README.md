# NFC writer with rich output

## これは何？

PyCon JP 2024の準備で使用するために作成したNFCリーダライタユーティリティです。
カメラでQRコードを読み取り、そのQRコードをデコードして得られるURIをNFCタグに書き込むことが出来ます。

![demo gif](https://github.com/user-attachments/assets/1956be69-70a9-45ed-aff1-19af2ffa8f66)

NFCリーダライタとしてSONYの[RC-S380](https://www.sony.co.jp/Products/felica/consumer/products/RC-S380.html)を使って動作確認済みです。

## 準備

Pythonプロジェクトマネージャーのuvを[Installation Guide](https://github.com/astral-sh/uv?tab=readme-ov-file#installation)に従ってインストールしてください。

次に、Windows環境の方は[nfcpyの公式ドキュメント](https://nfcpy.readthedocs.io/en/latest/topics/get-started.html)に従ってWinUSBとlibusbをインストールしてください。

> [!WARNING]
> Mac/Linux環境の場合はlibusbが標準でインストールされていますが、バージョンが1.0.0以上であることを確認してください。

最後に、以下に従ってこのリポジトリをcloneし、仮想環境を作成してください。

```bash
git clone https://github.com/t0d4/nfc-writer.git
cd nfc-writer
uv python install 3.11
uv sync
```

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