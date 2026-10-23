-- PostgreSQL 16+: lidmaatschap van app_user moet SET toestaan, anders faalt "SET LOCAL ROLE app_user".
-- Op Scaleway maakt de beheerlaag rollen aan als _rdb_superadmin, met ADMIN maar zonder SET; een kale
-- GRANT verandert daar niets aan. Daarom de opties expliciet.
DO $$ BEGIN
  IF current_setting('server_version_num')::int >= 160000 THEN
    EXECUTE format('GRANT app_user TO %I WITH INHERIT FALSE, SET TRUE', current_user);
  END IF;
END $$;
