# 0001 · Modulaire monoliet met domeinen

- Status: aangenomen
- Datum: 2026-10-22

## Besluit
Eén API (NestJS) met harde grenzen tussen domeinen. Elk domein heeft een eigen PostgreSQL-schema en een publieke interface. Domeinen lezen nooit elkaars tabellen en praten via interfaces of domeinevents. Een domein gaat pas apart draaien bij een meetbare reden.
