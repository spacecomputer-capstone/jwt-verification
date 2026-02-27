import { OrbitportSDK } from "@spacecomputer-io/orbitport-sdk-ts";

const clientId = process.env.OP_CLIENT_ID || "";
const clientSecret = process.env.OP_CLIENT_SECRET || "";

if (!clientId || !clientSecret) {
  console.error("Missing OP_CLIENT_ID or OP_CLIENT_SECRET");
  process.exit(1);
}

async function main() {
  const sdk = new OrbitportSDK({
    config: {
      clientId,
      clientSecret,
    },
  });

  const result = await sdk.ctrng.random();
  const hex = (
    result?.data?.data ??
    result?.data ??
    ""
  ).toString().trim().toLowerCase();
  if (!hex) {
    console.error("Orbitport returned empty cTRNG data");
    process.exit(1);
  }
  process.stdout.write(hex);
}

main().catch((err) => {
  console.error(String(err?.message || err));
  process.exit(1);
});
