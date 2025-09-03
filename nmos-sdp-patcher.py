#!/usr/bin/env python3

import sys
import json
import http.client
import urllib.parse
import os
import time
import argparse
from collections import OrderedDict

def http_get(host, port, path):
    conn = http.client.HTTPConnection(host, port)
    conn.request("GET", path)
    res = conn.getresponse()
    if res.status != 200:
        print(f"GET failed: {path} -> {res.status}")
        sys.exit(1)
    return res.read().decode()

def http_get_url(full_url):
    print(f"[DEBUG] manifest_href: {full_url}")
    parsed = urllib.parse.urlparse(full_url)
    host = parsed.hostname
    port = parsed.port or 80
    conn = http.client.HTTPConnection(host, port)
    conn.request("GET", parsed.path)
    res = conn.getresponse()
    if res.status != 200:
        print(f"GET failed: {full_url} -> {res.status}")
        sys.exit(1)
    return res.read().decode()

def http_patch(host, port, path, body):
    print("\n[PATCH送信内容]")
    print(json.dumps(json.loads(body), indent=2))

    conn = http.client.HTTPConnection(host, port)
    headers = {"Content-Type": "application/json"}
    conn.request("PATCH", path, body, headers)
    res = conn.getresponse()

    print(f"\n[PATCH Response] {res.status} {res.reason}")
    try:
        response_body = res.read().decode()
        print(response_body if response_body.strip() else "(No body)")
    except Exception as e:
        print(f"(レスポンス読み取りエラー: {e})")

    if res.status not in (200, 202):
        print(f"PATCH failed: {path} -> {res.status}")
        sys.exit(1)

def parse_sdp_to_json(sdp_text, sender_id=None, receiver_port_count=2):
    # 改行を正規化してから、CRLFを統一的に処理
    normalized_sdp = sdp_text.replace("\r\n", "\n").replace("\r", "\n")
    normalized_sdp_crlf = normalized_sdp.replace("\n", "\r\n")
    # 連続した空行（\r\n\r\n）を1つにまとめる
    normalized_sdp_crlf = normalized_sdp_crlf.replace("\r\n\r\n", "\r\n")

    lines = normalized_sdp.splitlines()

    result = OrderedDict()
    result["activation"] = {"mode": "activate_immediate"}
    result["master_enable"] = True
    if sender_id:
        result["sender_id"] = sender_id
    result["transport_file"] = {
        "data": normalized_sdp_crlf,
        "type": "application/sdp"
    }
    result["transport_params"] = []

    current_block = {
        "destination_port": None,
        "multicast_ip": None,
        "source_ip": None,
        "rtp_enabled": True
    }
    param_blocks = {}
    current_mid = None

    for line in lines:
        if line.startswith("m="):
            current_block["destination_port"] = int(line.split()[1])
        elif line.startswith("c=IN IP4"):
            current_block["multicast_ip"] = line.split()[2].split("/")[0]
        elif line.startswith("a=source-filter:"):
            current_block["source_ip"] = line.split()[-1]
        elif line.startswith("a=mid:"):
            current_mid = line.split(":")[1]
            param_blocks[current_mid] = current_block.copy()
            current_block = {
                "destination_port": None,
                "multicast_ip": None,
                "source_ip": None,
                "rtp_enabled": True
            }

    if param_blocks:
        if "primary" in param_blocks and "secondary" in param_blocks:
            result["transport_params"].append(param_blocks["primary"])
            result["transport_params"].append(param_blocks["secondary"])
        elif "primary" in param_blocks:
            result["transport_params"].append(param_blocks["primary"])
            result["transport_params"].append({"rtp_enabled": False})
        else:
            only_block = list(param_blocks.values())[0]
            result["transport_params"].append(only_block)
            result["transport_params"].append({"rtp_enabled": False})
    else:
        if all(v is not None for v in [current_block["destination_port"], current_block["multicast_ip"], current_block["source_ip"]]):
            result["transport_params"].append(current_block)
            result["transport_params"].append({"rtp_enabled": False})
        else:
            print("SDPからtransport_paramsを抽出できませんでした（必要な情報が不足しています）")
            sys.exit(1)

    if receiver_port_count == 1 and len(result["transport_params"]) > 1:
        result["transport_params"] = [result["transport_params"][0]]

    return result


def select_from_list(items, prompt="選択肢:"):
    print(f"\n{prompt}")
    for idx, item in enumerate(items):
        print(f"{idx + 1}: {item}")
    while True:
        try:
            choice = int(input("\n番号を入力してください: "))
            if 1 <= choice <= len(items):
                return choice - 1
            else:
                print("範囲外の番号です。")
        except ValueError:
            print("番号を入力してください。")

def test_patch_path(host, port, conn_ver, receiver_id):
    base = f"/x-nmos/connection/{conn_ver}/single/receivers/{receiver_id}/staged"
    for suffix in ["/", ""]:
        path = base + suffix
        try:
            http_patch(host, port, path, json.dumps({
                "activation": {"mode": "activate_immediate"},
                "master_enable": False
            }))
            print(f"[INFO] PATCH accepted at: {path}")
            active_path = f"/x-nmos/connection/{conn_ver}/single/receivers/{receiver_id}/active/"
            return path, active_path
        except SystemExit:
            print(f"[INFO] PATCH to {path} failed.")
    print("[ERROR] PATCH failed at both paths.")
    sys.exit(1)

def send_main_patch(host, port, path, json_body):
    print("\n[本番PATCH送信前のJSON]")
    print(json.dumps(json_body, indent=2))
    http_patch(host, port, path, json.dumps(json_body))

def main():
    parser = argparse.ArgumentParser(description="NMOS SDP Sender")

    parser.add_argument("sender", nargs="?", help="Sender IP[:port]（-sdpなしの場合に使用）")
    parser.add_argument("receiver", help="Receiver IP[:port]")
    parser.add_argument("-s", "--sdp", help="ローカルSDPファイルを送信に使用する")

    parser.add_argument("-rp04", "--receiver-port-04", type=int, help="IS-04用のReceiverポート番号")
    parser.add_argument("-rp05", "--receiver-port-05", type=int, help="IS-05用のReceiverポート番号")

    args = parser.parse_args()

    # 位置引数から receiver_host, receiver_port を抽出
    receiver_host, receiver_port = (args.receiver.split(":") + ["80"])[:2]
    receiver_port = int(receiver_port)

    receiver_port_04 = args.receiver_port_04 if args.receiver_port_04 else receiver_port
    receiver_port_05 = args.receiver_port_05 if args.receiver_port_05 else receiver_port

    # SDP読み込み or Senderから取得
    if args.sdp:
        if not os.path.exists(args.sdp):
            print(f"SDPファイルが見つかりません: {args.sdp}")
            sys.exit(1)
        with open(args.sdp, "r", encoding="utf-8") as f:
            sdp_text = f.read()
        sender_id = None
    else:
        if not args.sender:
            print("Sender IP[:port] または -s オプションを指定してください。")
            sys.exit(1)

        sender_host, sender_port = (args.sender.split(":") + ["80"])[:2]
        sender_port = int(sender_port)

        sender_versions = json.loads(http_get(sender_host, sender_port, "/x-nmos/node/"))
        sender_ver = sorted(sender_versions)[-1].strip("/")
        senders = json.loads(http_get(sender_host, sender_port, f"/x-nmos/node/{sender_ver}/senders/"))

        choices = [f'{s["label"]} ({s["id"]})' for s in senders]
        idx = select_from_list(choices, "SDPを取得するSenderを選んでください:")
        sender = senders[idx]
        sender_id = sender.get("id")

        manifest_href = sender.get("manifest_href")
        if not manifest_href:
            print("manifest_href が見つかりませんでした。")
            sys.exit(1)

        sdp_text = http_get_url(manifest_href)

    # IS-04（node API）でreceiver取得
    receiver_versions = json.loads(http_get(receiver_host, receiver_port_04, "/x-nmos/node/"))
    receiver_ver = sorted(receiver_versions)[-1].strip("/")
    receivers = json.loads(http_get(receiver_host, receiver_port_04, f"/x-nmos/node/{receiver_ver}/receivers/"))

    r_choices = [f'{r["label"]} ({r["id"]}) - {r["format"]}' for r in receivers]
    r_idx = select_from_list(r_choices, "SDPを送信するReceiverを選んでください:")
    receiver_id = receivers[r_idx]["id"]

    # IS-05（connection API）へ接続
    conn_versions = json.loads(http_get(receiver_host, receiver_port_05, "/x-nmos/connection/"))
    conn_ver = sorted(conn_versions)[-1].strip("/")

    patch_path, active_path = test_patch_path(receiver_host, receiver_port_05, conn_ver, receiver_id)

    active_json = json.loads(http_get(receiver_host, receiver_port_05, active_path))
    receiver_port_count = len(active_json.get("transport_params", []))

    json_body = parse_sdp_to_json(sdp_text, sender_id=sender_id, receiver_port_count=receiver_port_count)

    send_main_patch(receiver_host, receiver_port_05, patch_path, json_body)

    time.sleep(1)
    active_json = json.loads(http_get(receiver_host, receiver_port_05, active_path))
    print("\n[ReceiverのActive状態]")
    print(json.dumps(active_json, indent=2))


if __name__ == "__main__":
    main()
