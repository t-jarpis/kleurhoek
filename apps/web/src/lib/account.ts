/** Uitloggen vanuit de browser: sessie wissen en door naar Zitadel om daar ook uit te loggen. */
export async function logout(): Promise<void> {
  const res = await fetch("/auth/logout", { method: "POST" });
  const body = res.ok ? ((await res.json()) as { location?: string }) : {};
  window.location.assign(body.location ?? "/");
}
