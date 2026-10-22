import { getBff } from "@/lib/auth";

export async function GET(request: Request) {
  const bff = getBff();
  if (!bff) return new Response("Inloggen staat uit", { status: 404 });
  return bff.callback(request);
}
