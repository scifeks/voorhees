# voorhees

A REPL for slicing apart JWTs during security testing. Paste a token, get the decoded header, payload, and signature. Modify them iteratively and get a reassembled token after each change.

## Why

Online JWT tools work fine until you paste a production token into one. Voorhees runs entirely on your machine. Nothing leaves localhost, nothing gets logged by a third party, no accidents.

## Operations

Each change to the header or payload offers three modes:

**Replace** overwrites the entire segment with whatever JSON you paste in. Everything that was there before is gone. Think PUT.

**Merge** updates or adds individual keys without touching the rest of the segment. Think PATCH.

**Remove key** deletes a single key from the segment by name.

**Remove signature** strips the third segment and leaves the trailing dot, ready for `alg:none` and other signature validation tests.

All changes are cumulative. The reassembled token is printed after every operation.

## Example

```
$ python3 voorhees.py
Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InVzZXIiLCJhZG1pbiI6MH0.c2lnbmF0dXJl

Header:    {
  "typ": "JWT",
  "alg": "HS256"
}
Body:      {
  "username": "user",
  "admin": 0
}
Signature: c2lnbmF0dXJl

1) Change header  2) Change body  3) Remove signature  q) Quit
Choice: 1
1) Replace entire header  2) Merge segment  3) Remove key
Choice [1/2/3]: 2
Paste JSON: {"alg": "none"}

Header:    {
  "typ": "JWT",
  "alg": "none"
}
Body:      {
  "username": "user",
  "admin": 0
}
Signature: c2lnbmF0dXJl

JWT: eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJ1c2VybmFtZSI6InVzZXIiLCJhZG1pbiI6MH0.c2lnbmF0dXJl

1) Change header  2) Change body  3) Remove signature  q) Quit
Choice: 2
1) Replace entire body  2) Merge segment  3) Remove key
Choice [1/2/3]: 2
Paste JSON: {"admin": 1}

Header:    {
  "typ": "JWT",
  "alg": "none"
}
Body:      {
  "username": "user",
  "admin": 1
}
Signature: c2lnbmF0dXJl

JWT: eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJ1c2VybmFtZSI6InVzZXIiLCJhZG1pbiI6MX0.c2lnbmF0dXJl

1) Change header  2) Change body  3) Remove signature  q) Quit
Choice: 3

Header:    {
  "typ": "JWT",
  "alg": "none"
}
Body:      {
  "username": "user",
  "admin": 1
}
Signature: (removed)

JWT: eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJ1c2VybmFtZSI6InVzZXIiLCJhZG1pbiI6MX0.
```

## Requirements

Python 3.6+. No external dependencies.

## Disclaimer

For authorized security testing and educational use only.

## License

Unlicense
