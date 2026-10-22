"use client";

export function LogoutButton() {
  async function logout() {
    const res = await fetch("/auth/logout", { method: "POST" });
    const body = res.ok ? ((await res.json()) as { location?: string }) : {};
    window.location.assign(body.location ?? "/");
  }
  return <button type="button" className="ghost" onClick={() => void logout()}>Uitloggen</button>;
}
