// Draait tijdelijk in plaats van de API (workflow Diagnose, deep=true): controleert de database,
// draait migraties en seed met tijden, en toont het resultaat alleen met de eenmalige sleutel.
// Geen geheimen in de uitvoer.
const http = require("http");
const { Pool } = require("pg");
const lines = [];
const log = (s) => lines.push(`${new Date().toISOString()} ${s}`);
const ca = process.env.DATABASE_CA;
const describe = (e) => {
  const c = (e && e.cause) || e || {};
  const q = /Failed query: ([\s\S]{0,200})/.exec((e && e.message) || "");
  return [c.message || String(e), c.code && `code ${c.code}`, c.detail && `detail: ${c.detail}`, c.hint && `hint: ${c.hint}`, q && `query: ${q[1].replace(/\s+/g, " ")}`]
    .filter(Boolean).join(" | ");
};
(async () => {
  // Uitgaand verkeer: kan de API Zitadel bereiken (nodig om tokens van beheerders te controleren)?
  if (process.env.OIDC_ISSUER) {
    const t0 = Date.now();
    try {
      const r = await fetch(`${process.env.OIDC_ISSUER}/.well-known/openid-configuration`, { signal: AbortSignal.timeout(10000) });
      const j = await r.json();
      log(`zitadel ${r.status} in ${Date.now() - t0} ms; jwks ${j.jwks_uri}`);
      const k = await fetch(j.jwks_uri, { signal: AbortSignal.timeout(10000) });
      log(`jwks ${k.status} in ${Date.now() - t0} ms`);
    } catch (e) { log(`zitadel NIET bereikbaar na ${Date.now() - t0} ms: ${e.message}`); }
  }
  try {
    log("verbinden");
    const pool = new Pool({ connectionString: process.env.DATABASE_URL, ssl: ca ? { ca, checkServerIdentity: () => undefined } : undefined, connectionTimeoutMillis: 10000, max: 2 });
    const r = await pool.query(`select current_user as u, version() as v,
      (select rolcreaterole from pg_roles where rolname = current_user) as createrole,
      (select rolsuper from pg_roles where rolname = current_user) as super,
      (select count(*) from pg_locks where locktype = 'advisory') as advisory_locks,
      (select count(*) from pg_roles where rolname = 'app_user') as app_user,
      (select count(*) from information_schema.schemata where schema_name = 'drizzle') as drizzle_schema`);
    log(JSON.stringify(r.rows[0]));
    const m = await pool.query("select count(*) as n from drizzle.__drizzle_migrations").catch((e) => ({ rows: [{ n: `geen tabel (${e.message})` }] }));
    log(`toegepaste migraties: ${m.rows[0].n}`);
    const mem = await pool.query(`select r.rolname as role, g.rolname as grantor, m.admin_option, m.inherit_option, m.set_option
      from pg_auth_members m join pg_roles r on r.oid = m.roleid join pg_roles g on g.oid = m.grantor
      where m.member = (select oid from pg_roles where rolname = current_user)`).catch((e) => ({ rows: [`fout: ${e.message}`] }));
    log(`lidmaatschappen: ${JSON.stringify(mem.rows)}`);
    await pool.end();
    const { connectPostgres } = require("./dist/db/database");
    const h = connectPostgres(process.env.DATABASE_URL, { ca });
    log("migreren…"); await h.migrate(); log("migraties ok");
    const { seed } = require("./dist/db/seed");
    log("seed…"); const res = await seed(h.db, process.env.TENANT_ID); log(`seed ok ${JSON.stringify(res)}`);
    await h.close();
  } catch (e) {
    log(`FOUT ${describe(e)}`);
  }
  log("klaar");
})();
http.createServer((req, res) => {
  if (req.url === "/health") return res.end("ok");
  if (process.env.DIAG_KEY && req.url === `/diag?k=${process.env.DIAG_KEY}`) return res.end(lines.join("\n") + "\n");
  res.statusCode = 404; res.end();
}).listen(3001);
