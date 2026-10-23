-- De verbindingsrol moet app_user kunnen aannemen (SET ROLE). Op PostgreSQL 16+ krijgt de maker van
-- een rol daar niet vanzelf het recht toe, dus expliciet toekennen. Met de naam uitgeschreven in plaats
-- van CURRENT_USER: Scaleway Managed Database weigert "special role specifiers" in GRANT ... TO.
DO $$ BEGIN EXECUTE format('GRANT app_user TO %I', current_user); END $$;
