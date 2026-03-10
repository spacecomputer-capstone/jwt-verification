### Run Instructions (End-to-End)

1. Confirm backend is live:

- Open https://jwt-verification-sk0m.onrender.com/admin
- You should see the Pi dashboard page.

2. Clone repo on Pi and cd to rpi folder.

git clone https://github.com/spacecomputer-capstone/jwt-verification.git
cd jwt-verification/rpi
pip install -r requirements.txt

3. Generate Pi keypair (one-time) when at the base of the rpi folder:

openssl genrsa -out keys/pi_private.pem 2048
openssl rsa -in keys/pi_private.pem -pubout -out keys/pi_public.pem

4. Configure Orbitport creds at base of rpi folder (required for cTRNG):

export OP_CLIENT_ID="..."
export OP_CLIENT_SECRET="..."
sudo apt update
sudo apt install nodejs npm -y
npm install

Optional if the app will not be on the same network as the Pi:

export RPI_BRIDGE_ADVERTISED_URL="https://ervin-interglobular-selah.ngrok-free.dev"

5. Run Pi service:

python3 pi_client.py

Keep it running.

6. Wait ~2–3 seconds, then refresh:

- https://jwt-verification-sk0m.onrender.com/admin
- Confirm your Pi appears as ONLINE.

7. In the mobile app:

- Open mascot encounter screen.
- Tap Challenge.
- It should run JWT primary flow automatically (fallback only if needed).

———

### What Happens Internally (Mentor Given Sequence Mapping)

1. User -> Pi: user taps Challenge in app (request access).
2. Pi -> User: app gets signed challenge (cTRNG + Pi signature) from Pi bridge.
3. User signs cTRNG: app signs challenge locally (user key).
4. Forward signed info to backend: app sends {user_id, pi_id, challenge, pi_signature, user_signature} to backend.
5. Backend verify + issue/store JWT:

- verifies Pi signature + user signature

6. JWT used for access flow: app proceeds to catch flow as verified.

———

### Quick Troubleshooting

- Pi not showing in /admin:
    - check Pi script is still running
    - confirm same Render URL in rpi/config.py (BACKEND_URL)
- Invalid Pi signature:
    - regenerate pi_public.pem from current pi_private.pem, restart pi_client.py
- App falls back immediately:
    - Pi likely unreachable or backend verification failed; check /admin and Render logs.
    - if the app is on a different network than the Pi, ensure RPI_BRIDGE_ADVERTISED_URL points to a public URL that forwards to the Pi bridge
- Orbitport cTRNG failed:
      - check OP_CLIENT_ID / OP_CLIENT_SECRET are set in the same shell
      - run node scripts/get_ctrng.mjs from rpi/ to verify output hex
      - ensure internet access from Pi
