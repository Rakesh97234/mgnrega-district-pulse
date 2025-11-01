#!/bin/bash
set -e
GEOJSON="$1"
if [ -z "$GEOJSON" ]; then
  echo "Usage: $0 /path/to/karnataka_districts.geojson"
  exit 1
fi
echo "Importing $GEOJSON into PostGIS..."
PG="PG:host=localhost user=postgres dbname=mgnrega password=postgres"
ogr2ogr -f "PostgreSQL" "$PG" "$GEOJSON" -nln districts -append -lco GEOMETRY_NAME=geom -lco FID=gid -t_srs EPSG:4326
echo "Done."
