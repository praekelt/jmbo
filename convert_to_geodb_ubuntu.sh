#!/bin/bash

# Get arguments
echo -n "Enter your database name: "
read DB
echo "Select the database server you are using:"
echo "(1) PostgreSQL"
echo "(2) SQLite"
echo "(3) Other"
echo -n ""
read DB_TYPE

read -p "Installing required packages. Existing packages will not be upgraded to newer versions. [enter]" y
sudo apt-get install libproj0 libproj-dev libgeos-3.2.2 libgdal1-dev \
libgdal1-1.7.0 libgeoip1 libgeoip-dev --no-upgrade

if [ $DB_TYPE == 1 ]; then
    sudo apt-get install postgis postgresql-9.1-postgis --no-upgrade

    POSTGIS_SQL=postgis.sql

    # For Ubuntu 8.x and 9.x releases.
    if [ -d "/usr/share/postgresql-8.3-postgis" ]
    then
        POSTGIS_SQL_PATH=/usr/share/postgresql-8.3-postgis
        POSTGIS_SQL=lwpostgis.sql
    fi

    # For Ubuntu 10.04
    if [ -d "/usr/share/postgresql/8.4/contrib" ]
    then
        POSTGIS_SQL_PATH=/usr/share/postgresql/8.4/contrib
    fi

    # For Ubuntu 10.10 (with PostGIS 1.5)
    if [ -d "/usr/share/postgresql/8.4/contrib/postgis-1.5" ]
    then
        POSTGIS_SQL_PATH=/usr/share/postgresql/8.4/contrib/postgis-1.5
    fi

    # For Ubuntu 11.10 / Linux Mint 12 (with PostGIS 1.5)
    if [ -d "/usr/share/postgresql/9.1/contrib/postgis-1.5" ]
    then
        POSTGIS_SQL_PATH=/usr/share/postgresql/9.1/contrib/postgis-1.5
    fi

    sudo -u postgres psql -d $DB -f $POSTGIS_SQL_PATH/$POSTGIS_SQL
    sudo -u postgres psql -d $DB -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
    sudo -u postgres psql -d $DB -c "GRANT ALL ON geometry_columns TO PUBLIC;"
    sudo -u postgres psql -d $DB -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
   
    echo "PostGIS SQL installed"
fi

if [ $DB_TYPE == 2 ]; then
    sudo apt-get install sqlite3 libspatialite3 --no-upgrade

    sqlite3 $DB "SELECT load_extension('libspatialite.so'); SELECT InitSpatialMetadata();"

    echo "Spatialite SQL installed"
fi
