#!/usr/bin/env python3
"""wot-oracle: compute WoT scores, publish kind:30000 list."""
import argparse, json, os, websocket, ssl

RELAYS = ["wss://relay.damus.io","wss://nos.lol"]

def _sslopt():
    # TLS certificate verification is ON by default. Set WOT_INSECURE=1 only
    # for local testing against a self-signed relay — never in production:
    # disabling verification exposes the relay input to MITM tampering,
    # which directly corrupts the WoT scores this oracle publishes.
    if os.environ.get("WOT_INSECURE") == "1":
        return {"cert_reqs": ssl.CERT_NONE}
    return {}

def get_follows(pubkey):
    ws = websocket.create_connection(RELAYS[0], sslopt=_sslopt())
    ws.send(json.dumps(["REQ","f",{"kinds":[3],"authors":[pubkey]}]))
    follows = set()
    for _ in range(10):
        try:
            m = json.loads(ws.recv())
            if m[0]=="EVENT":
                # kind:3 follow list lives in the event's p-tags, not in
                # `content` (the legacy JSON-in-content format is deprecated
                # and most modern clients publish empty content).
                follows = set(t[1] for t in m[2].get("tags", []) if len(t) > 1 and t[0] == "p")
        except: break
    ws.close(); return follows

def wot_score(pubkey, trusted, follows_map):
    f = follows_map.get(pubkey, set())
    return len(f & trusted) / max(len(trusted),1)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--seeds", nargs="+", required=True)
    a = ap.parse_args()
    trusted = set(a.seeds)
    fm = {s: get_follows(s) for s in a.seeds}
    # score the union of all followed keys
    candidates = set().union(*fm.values())
    scored = {c: round(wot_score(c, trusted, fm),3) for c in candidates}
    scored = dict(sorted(scored.items(), key=lambda x:-x[1]))
    with open("wot_scores.json","w") as f: json.dump(scored, f, indent=2)
    print(f"[wot] scored {len(scored)} pubkeys; top: {list(scored)[:5]}")

if __name__ == "__main__":
    main()
