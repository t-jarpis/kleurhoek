// Organisatiedomeinen van Kleurhoek (ADR 0017): {code}.kleurhoek.nl en {code}-dev.kleurhoek.nl.
// Stuurt het verzoek door naar de website van de omgeving en geeft de oorspronkelijke host, het
// IP-adres en het land mee. De website vertrouwt die alleen met WORKER_SECRET_<ENV>; EDGE_SECRET_<ENV>
// is de gewone geheime header waarmee de container verkeer van buiten Cloudflare weigert.
// Configuratie (ROUTES, als tekst): [{ "env": "dev", "suffix": "-dev.kleurhoek.nl", "origin": "dev.kleurhoek.nl" }, …]
// De langste suffix wint, dus "-dev.kleurhoek.nl" vóór ".kleurhoek.nl".
// Daarnaast de domeinen per land (ADR 0040): HOSTS (als tekst) koppelt een vaste host aan een omgeving,
// bijvoorbeeld { "www.kleurhoek.be": "prod", "dev.kleurhoek.com": "dev" }. Die gaan zonder code door.

const CODE = /^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$/;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const host = url.hostname.toLowerCase();
    const routes = JSON.parse(env.ROUTES).sort((a, b) => b.suffix.length - a.suffix.length);
    const fixed = JSON.parse(env.HOSTS ?? "{}")[host];
    const route = fixed ? routes.find((r) => r.env === fixed) : routes.find((r) => host.endsWith(r.suffix));
    const code = route && !fixed ? host.slice(0, -route.suffix.length) : "";
    if (!route || (!fixed && !CODE.test(code))) return new Response("Onbekend adres", { status: 404, headers: { "content-type": "text/plain; charset=utf-8" } });

    const target = new URL(url);
    target.hostname = route.origin;
    const headers = new Headers(request.headers);
    for (const h of ["x-kh-host", "x-kh-client-ip", "x-kh-country", "x-kh-worker"]) headers.delete(h);
    headers.set("x-kh-host", host);
    headers.set("x-kh-client-ip", request.headers.get("cf-connecting-ip") ?? "");
    headers.set("x-kh-country", request.headers.get("cf-ipcountry") ?? "");
    headers.set("x-kh-worker", env[`WORKER_SECRET_${route.env.toUpperCase()}`]);
    headers.set("x-kleurhoek-edge", env[`EDGE_SECRET_${route.env.toUpperCase()}`]);

    const res = await fetch(new Request(target, { method: request.method, headers, body: request.body, redirect: "manual" }));

    // Doorverwijzingen naar de website zelf terugzetten naar het domein van de bezoeker. Niet als de website
    // bewust naar een ander eigen domein stuurt (x-kh-keep-location, ADR 0040).
    const location = res.headers.get("location");
    if (!location) return res;
    if (res.headers.get("x-kh-keep-location")) { const out = new Response(res.body, res); out.headers.delete("x-kh-keep-location"); return out; }
    const loc = new URL(location, target);
    if (loc.hostname !== route.origin) return res;
    loc.hostname = host;
    const out = new Response(res.body, res);
    out.headers.set("location", loc.toString());
    return out;
  },
};
