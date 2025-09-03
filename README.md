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

機器に使用するアドレス、ポートが分からない場合は、
Nmapなどのツールを使用して空いているポートを調査し、確認できたポートにWebアクセスして、以下のエンドポイントに接続できるかどうかを確認してください。

If you do not know the address or port used for the device,
Use a tool such as Nmap to investigate available ports, and then use web access to the confirmed ports to see if you can connect to the following endpoints

Sender: http://xx.xx.xx.xx:[port]/x-nmos/node
Receiver: http://xx.xx.xx.xx:[port]/x-nmos/connection

---
##  リリースノート（v1.1）
"Support devices where the port numbers of IS-04 and IS-05 are different."
IS-04とIS-05のポートナンバーの違うデバイスに対応しました。

python3 nmos-sdp-patcher.py <sender_ip[:port]> -rp04<node_port[:port]> -rp05<connection_port[:port]> <receiver_ip[:port]>


---
## 🚀 リリースファイル（v1.1.0）
🗂️ Assets:
- [📦 nmos-sdp-patcher_x64.exe](https://github.com/taqq505/nmos-sdp-patcher/releases/download/v1.1/nmos-sdp-patcher_x64_v1.1.exe)
- [📁 Source code (zip)](https://github.com/taqq505/nmos-sdp-patcher/archive/refs/tags/v1.1.zip)
- [📁 Source code (tar.gz)](https://github.com/taqq505/nmos-sdp-patcher/archive/refs/tags/v1.1.tar.gz)
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

python3 nmos-sdp-patcher.py <sender_ip[:port]> <receiver_ip[:port]> 

python3 nmos-sdp-patcher.py 10.1.2.20:8080 10.1.2.10:9080

python3 nmos-sdp-patcher.py -s <sdp_file> <receiver_ip[:port]> 

python3 nmos-sdp-patcher.py --sdp <sdp_file> <receiver_ip[:port]> 

python3 nmos-sdp-patcher.py -s ./SDP.sdp 10.1.2.20:8080 

---






📄 ライセンス / License
MIT License
