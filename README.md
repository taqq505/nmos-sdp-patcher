# 🛰️ NMOS SDP Get & Load Utility

![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)
![NMOS](https://img.shields.io/badge/NMOS-IS--04-informational)
![NMOS](https://img.shields.io/badge/NMOS-IS--05-informational)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

NMOS IS-05 機器に対して SDP ファイルを送信（PATCH）するためのユーティリティです。

This is a utility to push SDP files to NMOS IS-05 compatible receivers via PATCH.

コンセプトは軽量・簡易・ノーセットアップです。RDSを構築する必要はありません。

The concept is lightweight, simple, and zero-setup.

There is no need to build or deploy an RDS.

このアプリ自体がsenderにアクセスし、SDPを選択取得できます。

ラボ用途など、システムに組み込まれていないデバイスの簡易操作でご活用ください。

This application directly accesses the sender and allows you to select and retrieve SDP files.

It is intended for easy operation of devices that are not part of a larger system, such as for use in lab environments.

Nmapなどのツールを使用して空いているポートを調査し、確認できたポートにWebアクセスして、以下のエンドポイントに接続できるかどうかを確認してください。

Please use tools like Nmap to scan for open ports, and then access those ports via a web browser to verify whether the following endpoints are accessible.


Sender: http://xx.xx.xx.xx:[port]/x-nmos/node

Receiver: http://xx.xx.xx.xx:[port]/x-nmos/connection

---

## ✨ 特長 / Features

- ✅ NMOS Sender から SDP を自動取得
- ✅ ローカルSDPファイルの送信にも対応（`-s` or `--sdp` オプション）
- ✅ ST2022-7 非対応機器にも自動対応
- ✅ `"sender_id"` 省略可能、指定可能
- ✅ `activation.mode = "activate_immediate"` 固定
- ✅ 
---

## 📦 インストール不要 / No Installation Needed

Python 3.x 環境でそのまま実行可能です（追加ライブラリ不要）。
Ubuntu24.04のPython環境の仮想必須化に対応し、モジュールはすべて標準搭載のものだけを使用しています。

No dependencies required — works with standard Python 3.
In response to the virtual environment requirement, all modules are used only as standard equipment.
---

## 🚀 使い方 / Usage

### ▶️ SenderからSDPを取得して送信（自動）

python3 nmos-sdp-patcher.py <sender_ip[:port]> <receiver_ip[:port]>

例 / Example:

python3 nmos-sdp-patcher.py 10.1.2.20 10.1.2.10

python3 nmos-sdp-patcher.py -s <sdp_file> <receiver_ip[:port]> 

python3 nmos-sdp-patcher.py --sdp <sdp_file> <receiver_ip[:port]> 

📄 ライセンス / License
MIT License
