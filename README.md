# 🛰️ NMOS SDP Get & Load Utility

![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)
![NMOS](https://img.shields.io/badge/NMOS-IS--05-informational)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

NMOS IS-05 機器に対して SDP ファイルを送信（PATCH）するためのユーティリティです。  
This is a utility to push SDP files to NMOS IS-05 compatible receivers via PATCH.

---

## ✨ 特長 / Features

- ✅ NMOS Sender から SDP を自動取得
- ✅ ローカルSDPファイルの送信にも対応（`-s` or `--sdp` オプション）
- ✅ ST2022-7 非対応機器にも自動対応
- ✅ `"sender_id"` 省略可能、指定可能
- ✅ `activation.mode = "activate_immediate"` 固定

---

## 📦 インストール不要 / No Installation Needed

Python 3.x 環境でそのまま実行可能です（追加ライブラリ不要）。
仮想環境必須化に対応し、モジュールはすべて標準搭載のものだけを使用しています。

No dependencies required — works with standard Python 3.
In response to the virtual environment requirement, all modules are used only as standard equipment.
---

## 🚀 使い方 / Usage

### ▶️ SenderからSDPを取得して送信（自動）

python3 nmos-sdp-get-load.py <receiver_ip[:port]> <sender_ip[:port]>
例 / Example:

python3 nmos-sdp-get-load.py 10.1.2.20 10.1.2.10

python3 nmos-sdp-get-load.py <receiver_ip[:port]> -s <sdp_file>

python3 nmos-sdp-get-load.py <receiver_ip[:port]> --sdp <sdp_file>

📄 ライセンス / License
MIT License
