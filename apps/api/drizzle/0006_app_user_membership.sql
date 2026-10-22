-- De verbindingsrol moet app_user kunnen aannemen (SET ROLE). Op Azure PostgreSQL 16+ krijgt de maker
-- van een rol daar niet vanzelf het recht toe, dus expliciet toekennen.
GRANT app_user TO CURRENT_USER;
