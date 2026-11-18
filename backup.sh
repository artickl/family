#!/bin/bash

# Configuration
BACKUP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="grampsweb_celery"
EXPORT_DIR="$BACKUP_DIR/export"
EXPORT_FILE="family_tree.csv"
DB_CONFIG="--config=database.path:/root/.gramps/grampsdb"
FAMILY="-O /root/.gramps/grampsdb/2735de88-9bd2-416e-ae2e-e0c4a3a4b90d"
FORMAT="-f csv -y"

# 1. Export the family tree to uncompressed Gramps XML inside the Git repo as CSV
docker exec grampsweb_celery gramps $DB_CONFIG $FAMILY -e "/tmp/$EXPORT_FILE" $FORMAT
docker cp grampsweb_celery:/tmp/$EXPORT_FILE $EXPORT_DIR/$EXPORT_FILE

# 2. Split family_tree.csv to family_tree_places.csv, family_tree_persons.csv, family_tree_marriages.csv, family_tree_families.csv
python3 "$BACKUP_DIR/split_csv.py" "$EXPORT_DIR/$EXPORT_FILE" "$EXPORT_DIR"

# 3. Navigate to your Git repository
cd $BACKUP_DIR

# 4. Commit and push to your remote Git server (GitHub, Gitea, etc.)
#git add *
#git commit -m "Automated backup: $(date +'%Y-%m-%d %H:%M:%S')"
#git push origin main
