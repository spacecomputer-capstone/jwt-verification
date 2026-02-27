# JWT Presence Flow (Mentor Sequence)

This repo now follows this exact challenge-signature-JWT sequence:

1. User -> Pi: asks for access.
2. Pi -> User: sends fresh `cTRNG` challenge with Pi signature.
3. User -> Pi: sends signature over `cTRNG`.
4. Pi -> Backend: forwards `{user_id, pi_id, challenge, pi_signature, user_signature}`.
5. Backend: verifies both signatures, mints JWT, stores session in DB.
6. Backend -> Pi -> User: JWT is returned and forwarded.

## Key Setup (once)

Backend keys:
- `jwt-flask/keys/backend_private.pem`
- `jwt-flask/keys/backend_public.pem`

Pi keys:
- `rpi/keys/pi_private.pem`
- `rpi/keys/pi_public.pem`
- Copy Pi public key to backend: `jwt-flask/keys/pi_keys/pi1_pub.pem`

User keys:
- `user/keys/user1_private.pem` (private key stays on user client)
- `user/keys/pi_public.pem` (for verifying Pi's challenge signature)
- Copy user public key to backend: `jwt-flask/keys/user_keys/user1_pub.pem`

## Run Backend

```bash
cd jwt-flask
pip install -r requirements.txt
python3 app.py
```

## App Integration Mode (phone + Pi)

Set this env var on backend to allow Pi-only proof (no separate `user_client`):

```bash
REQUIRE_USER_SIGNATURE=false
```

Then run:

```bash
# terminal 1 (backend)
cd jwt-flask
pip install -r requirements.txt
python3 app.py
```

```bash
# terminal 2 (rpi)
cd rpi
pip install -r requirements.txt
python3 pi_client.py
```

Pi prints a JSON packet with:
- `pi_id`
- `challenge`
- `pi_signature`

In your app JWT dialog:
1. Paste `pi_id`, `challenge`, `pi_signature` from Pi output.
2. Leave `user_signature` empty (only in Pi-only demo mode).
3. Submit; app calls `POST /presence/exchange` and receives JWT.

## Strict Mentor Mode (user + Pi signatures)

```bash
# terminal 1 (user)
cd user
pip install -r requirements.txt
python3 user_client.py
```

```bash
# terminal 2 (rpi)
cd rpi
pip install -r requirements.txt
python3 pi_client.py
```

Flow:
1. Pi prints a JSON challenge packet.
2. Paste that JSON into `user_client.py`.
3. User client verifies Pi signature and prints `user_signature=<hex>`.
4. Paste the hex back into Pi client.
5. Use that `user_signature` when calling backend.

## Backend Endpoint

- `POST /presence/exchange`

Request body:

```json
{
  "user_id": "user1",
  "pi_id": "pi1",
  "challenge": "<hex challenge>",
  "pi_signature": "<hex signature by Pi private key>",
  "user_signature": "<hex signature by User private key (optional when REQUIRE_USER_SIGNATURE=false)>"
}
```

Response:

```json
{
  "presence_jwt": "<jwt>",
  "sid": "<session-id>"
}
```
