#!/usr/bin/env python3

import sys
import json
import http.client
import urllib.parse
import time
from collections import OrderedDict
import argparse
import os

def http_get(host, port, path):
    conn = http.client.HTTPConnection(host, port)
    conn.request("GET", path)
    res = conn.getresponse()
    if res.status != 200:
        print(f"GET failed: {path} -> {res.status}")
        sys.exit(1)
    return res.read().decode()

def http_get_url(full_url):
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
    normalized_sdp = sdp_text.replace("\r\n", "\n").replace("\r", "\n")
    normalized_sdp_crlf = normalized_sdp.replace("\n", "\r\n")
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
            result["transport_params"].append({ "rtp_enabled": False })
        else:
            only_block = list(param_blocks.values())[0]
            result["transport_params"].append(only_block)
            result["transport_params"].append({ "rtp_enabled": False })
    else:
        if all(v is not None for v in [current_block["destination_port"], current_block["multicast_ip"], current_block["source_ip"]]):
            result["transport_params"].append(current_block)
            result["transport_params"].append({ "rtp_enabled": False })
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

def main():
    parser = argparse.ArgumentParser(description="NMOS SDP Sender")
    parser.add_argument("sender", nargs="?", help="Sender IP[:port]（-sdpなしの場合に使用）")
    parser.add_argument("receiver", help="Receiver IP[:port]")
    parser.add_argument("-s", "--sdp", help="ローカルSDPファイルを送信に使用する")
    args = parser.parse_args()

    receiver_host, receiver_port = (args.receiver.split(":") + ["80"])[:2]
    receiver_port = int(receiver_port)

    if args.sdp:
        # ローカルSDPモード
        if not os.path.exists(args.sdp):
            print(f"SDPファイルが見つかりません: {args.sdp}")
            sys.exit(1)

        with open(args.sdp, "r", encoding="utf-8") as f:
            sdp_text = f.read()
        sender_id = None  # 指定しない
    else:
        if not args.sender:
            print("Sender IP[:port] または -sdp オプションを指定してください。")
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

    # Receiver選択
    receiver_versions = json.loads(http_get(receiver_host, receiver_port, "/x-nmos/node/"))
    receiver_ver = sorted(receiver_versions)[-1].strip("/")
    receivers = json.loads(http_get(receiver_host, receiver_port, f"/x-nmos/node/{receiver_ver}/receivers/"))

    r_choices = [f'{r["label"]} ({r["id"]}) - {r["format"]}' for r in receivers]
    r_idx = select_from_list(r_choices, "SDPを送信するReceiverを選んでください:")
    receiver_id = receivers[r_idx]["id"]

    conn_versions = json.loads(http_get(receiver_host, receiver_port, "/x-nmos/connection/"))
    conn_ver = sorted(conn_versions)[-1].strip("/")
    patch_path = f"/x-nmos/connection/{conn_ver}/single/receivers/{receiver_id}/staged/"
    active_path = f"/x-nmos/connection/{conn_ver}/single/receivers/{receiver_id}/active/"

    # Receiverのactive情報取得 → ポート数確認
    active_json = json.loads(http_get(receiver_host, receiver_port, active_path))
    receiver_port_count = len(active_json.get("transport_params", []))

    # JSON作成
    json_body = parse_sdp_to_json(sdp_text, sender_id=sender_id, receiver_port_count=receiver_port_count)

    print("\n[送信予定のJSON]")
    print(json.dumps(json_body, indent=2))

    http_patch(receiver_host, receiver_port, patch_path, json.dumps(json_body))

    time.sleep(1)
    active_json = json.loads(http_get(receiver_host, receiver_port, active_path))
    print("\n[ReceiverのActive状態]")
    print(json.dumps(active_json, indent=2))

if __name__ == "__main__":
    main()
