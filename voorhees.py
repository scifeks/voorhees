#!/usr/bin/env python3
import json
import sys

import jwt


def display(header, body, signature):
    """Print the decoded JWT segments in a readable format."""
    print(f"\nHeader:    {json.dumps(header, indent=2)}")
    print(f"Body:      {json.dumps(body, indent=2)}")
    sig_display = signature if signature else "(removed)"
    print(f"Signature: {sig_display}")


def encode_token(header, body, signature):
    """Reassemble the JWT from current header, body, and signature state."""
    token = jwt.encode(body, key="", algorithm="none", headers=header)
    # jwt.encode with alg:none gives us header.body. — replace signature portion
    parts = token.split(".")
    return f"{parts[0]}.{parts[1]}.{signature}"


def replace_or_merge(current, label):
    """Prompt the user to replace, merge into, or remove a key from a segment."""
    mode = input(f"1) Replace entire {label}  2) Merge segment  3) Remove key\nChoice [1/2/3]: ").strip()
    if mode == "3":
        key = input("Key to remove: ").strip()
        current.pop(key, None)
        return current
    paste = input("Paste JSON: ").strip()
    try:
        incoming = json.loads(paste)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return current
    if mode == "1":
        return incoming
    current.update(incoming)
    return current


SUPPORTED_ALGS = [
    "HS256", "HS384", "HS512",
    "RS256", "RS384", "RS512",
    "ES256", "ES384", "ES512",
    "PS256", "PS384", "PS512",
]


def load_key(alg):
    """Prompt for a signing key appropriate to the algorithm."""
    if alg.startswith("HS"):
        return input("Secret key: ").strip()
    path_or_pem = input("Path to PEM private key (or paste it): ").strip()
    try:
        return open(path_or_pem, "r").read()
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return path_or_pem


def sign_token(header, body):
    """Re-sign the token using the alg in the header and a user-provided key."""
    alg = header.get("alg", "")
    if alg not in SUPPORTED_ALGS:
        print(f"Unsupported alg: {alg}", file=sys.stderr)
        print(f"Supported: {', '.join(SUPPORTED_ALGS)}", file=sys.stderr)
        return None
    key = load_key(alg)
    try:
        token = jwt.encode(body, key=key, algorithm=alg, headers=header)
        return token.split(".")[2]
    except Exception as e:
        print(f"Signing failed: {e}", file=sys.stderr)
        return None


def modify_signature(header, body, signature):
    """Prompt the user to remove or re-sign the signature."""
    mode = input("1) Remove signature  2) Re-sign with key\nChoice [1/2]: ").strip()
    if mode == "1":
        return ""
    if mode == "2":
        new_sig = sign_token(header, body)
        if new_sig is not None:
            return new_sig
    return signature


def main():
    """Interactive REPL for decoding, modifying, and reassembling JWTs."""
    token = input("Token: ").strip()
    parts = token.split(".")
    if len(parts) != 3:
        print("Not a valid JWT (expected 3 dot-separated segments).", file=sys.stderr)
        sys.exit(1)

    header = jwt.get_unverified_header(token)
    body = jwt.decode(token, options={"verify_signature": False}, algorithms=SUPPORTED_ALGS + ["none"])
    signature = parts[2]

    display(header, body, signature)

    while True:
        print("\n1) Change header  2) Change body  3) Signature  q) Quit")
        choice = input("Choice: ").strip().lower()

        if choice == "q":
            break
        elif choice == "1":
            header = replace_or_merge(header, "header")
        elif choice == "2":
            body = replace_or_merge(body, "body")
        elif choice == "3":
            signature = modify_signature(header, body, signature)
        else:
            continue

        display(header, body, signature)
        print(f"\nJWT: {encode_token(header, body, signature)}")


if __name__ == "__main__":
    main()
