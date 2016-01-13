/**
 * Database script that ensures that the db server AKRR will be using has the required databases and users w/
 * the required permissions before further setup occurs.
 */

# ENSURE: That the `mod_akrr` database is created.
CREATE DATABASE IF NOT EXISTS mod_akrr;

# ENSURE: That the `mod_appkernel` database is created.
CREATE DATABASE IF NOT EXISTS mod_appkernel;

# ENSURE: That the user that will be used by AKRR is created with the correct privileges.
GRANT ALL ON mod_akrr.* TO __AKRR_USER IDENTIFIED BY '__AKRR_USER_PASSWORD';

# ENSURE: That the AKRR user has the correct privileges to the `mod_appkernel` database.
GRANT ALL ON mod_appkernel.* TO __AKRR_USER IDENTIFIED BY '__AKRR_USER_PASSWORD';

# ENSURE: That the AKRR modw user is created w/ the correct privileges
GRANT SELECT ON modw.resourcefact TO __AKRR_MODW_USER IDENTIFIED BY '__AKRR_MODW_USER_PASSWORD';

# ENSURE: That the newly granted privileges are flushed into active service.
FLUSH PRIVILEGES;
