// Eén logregel per verzoek (methode, pad zonder query, status, duur, bytes) voor de Next.js-servers.
// Geen IP-adressen, cookies of query's: alleen wat nodig is om fouten te vinden (Cockpit, Diagnose).
// Gebruik: node -r ./request-log.cjs server.js
const http = require("node:http");
const emit = http.Server.prototype.emit;
http.Server.prototype.emit = function (event, req, res) {
  if (event === "request" && req && res) {
    const start = process.hrtime.bigint();
    const path = (req.url || "").split("?")[0].slice(0, 200);
    if (!path.startsWith("/_next/static") && path !== "/healthz") {
      let bytes = 0;
      const write = res.write, end = res.end;
      res.write = function (chunk, ...rest) { if (chunk) bytes += Buffer.byteLength(chunk); return write.call(this, chunk, ...rest); };
      res.end = function (chunk, ...rest) { if (chunk && typeof chunk !== "function") bytes += Buffer.byteLength(chunk); return end.call(this, chunk, ...rest); };
      res.on("close", () => {
        const ms = Number(process.hrtime.bigint() - start) / 1e6;
        process.stdout.write(`${JSON.stringify({ req: req.method, path, status: res.statusCode, ms: Math.round(ms), bytes, done: res.writableFinished, hdr: (req.rawHeaders || []).reduce((n, v, i) => (i % 2 ? n + v.length : n), 0) })}\n`);
      });
    }
  }
  // Verzoeken die Node al weigert vóór de app ze ziet (bijv. 431: headers/cookies te groot). Die
  // geven anders een lege pagina zonder enige logregel.
  if (event === "clientError" && req) {
    process.stdout.write(`${JSON.stringify({ clientError: req.code || String(req.message).slice(0, 80), bytes: req.rawPacket ? req.rawPacket.length : undefined, limit: http.maxHeaderSize })}\n`);
  }
  return emit.apply(this, arguments);
};
