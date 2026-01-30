# JWT

1) Generate keys (once)
- Backend: create `backend_private.pem` + `backend_public.pem` in `jwt-flask/keys/`
- Pi: create `pi_private.pem` + `pi_public.pem` in `rpi/keys/`
- Copy Pi public key to backend: `jwt-flask/keys/pi_keys/pi1_pub.pem`

2) Run backend
- `cd jwt-flask`
- `pip install -r requirements.txt`
- `python app.py`

3) Mint JWT (phone/client)
- `POST /presence/start` with `{ "user_id": "...", "pi_id": "pi1" }`
- Receive `presence_jwt`

4) Send JWT to Pi
- Phone writes `presence_jwt` to Pi over BLE (Pi must be running).

5) Run Pi verifier
- On Raspberry Pi (Linux): `cd rpi`
- `pip install -r requirements.txt`
- `python3 pi_client.py`
- Pi verifies JWT, runs rounds, signs attestation, then calls `POST /presence/verify`

6) Backend returns result
- Backend verifies Pi signature + stores proof (SQLite)
- Returns `PASS/FAIL`