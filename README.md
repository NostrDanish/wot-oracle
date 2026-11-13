# wot-oracle

A small Python prototype for calculating a simple follow-graph overlap score from a set of trusted Nostr seed accounts.

## Current behavior

1. Accepts trusted seed public keys as 64-character hex strings.
2. Fetches each seed's kind-3 contact list from the first configured relay in oracle.py (currently relay.damus.io; TLS certificate verification is enabled by default).
3. Scores each candidate public key by the fraction of trusted seeds that follow that candidate.
4. Writes the result to wot_scores.json, sorted by score descending and pubkey ascending for stable output.

For candidate c and trusted seed set S:

score(c) = count(s in S where c is in follows(s)) / |S|

Scores are rounded to three decimal places in the output.

## Important limitations

This is **not yet a production Web-of-Trust provider**.

- It does not currently parse or apply NIP-32 labels, despite the original README wording.
- It does not yet verify the signatures of fetched kind-3 events.
- It currently queries only the first relay in RELAYS; it does not implement multi-relay reconciliation.
- It writes a local JSON file only. It does **not** publish kind-30000 lists or NIP-85 Trusted Assertions (kinds 30382–30385), and it does not publish a kind-10040 provider declaration.
- It has no production key management, provider key rotation, abuse controls or independent trust-policy review.

Do not configure this prototype as a trusted NIP-85 provider or use its output for access-control decisions until those gaps are closed and the provider is independently reviewed.

## Run locally

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 oracle.py --seeds <64-character-hex-pubkey> <another-hex-pubkey>
```

The script writes wot_scores.json in the current working directory.

## TLS safety

TLS certificate verification is on by default. WOT_INSECURE=1 disables certificate verification only for local testing against a self-signed relay. Never set this in production: a man-in-the-middle could alter the follow graph used to calculate scores.

## Standards direction

The intended interoperable output is NIP-85 Trusted Assertions, not a custom kind-30000 ranked list. NIP-85 requires provider keys and relays to be declared in the user's kind-10040 list. The publishing/signing path is not implemented yet; no private key is required or read by the current offline scoring step.
