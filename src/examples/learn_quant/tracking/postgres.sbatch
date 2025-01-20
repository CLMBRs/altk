#!/bin/bash
#SBATCH --job-name=postgres_db
#SBATCH --output=postgres_db.out
#SBATCH --error=postgres_db.err
#SBATCH --time=5-00
#SBATCH --partition=gpu-l40
#SBATCH --requeue
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=10G
#SBATCH --cpus-per-task=10
#SBATCH --nodelist=g3115

module load apptainer

apptainer cache clean

# Load environment variables from .env file
if [ -f .env_postgres ]; then
    export $(grep -v '^#' .env_postgres | xargs)
else
    echo "ERROR: .env_postgres file not found. Please create one with the necessary environment variables."
    exit 1
fi

# Function to log messages with timestamps and prefixes
log() {
  local prefix="$1"
  shift
  local message="$*"
  date +"%Y-%m-%d %H:%M:%S [$prefix] ${message}" >> "$LOG_FILE"
}

# Create directories
mkdir -p "$PGDATA_DIR" "$RUN_DIR"
log "MAIN" "Created directories: $PGDATA_DIR and $RUN_DIR"

# Check if the database needs initialization and initialize if needed
if [[ ! -f "$PGDATA_DIR/PG_VERSION" ]]; then
    log "INIT" "Initializing PostgreSQL database..."
    export POSTGRES_PASSWORD="$PG_PASSWORD"
    apptainer exec \
        -B "${PGDATA_DIR}:/var/lib/postgresql/data" \
        -B "${RUN_DIR}:/var/run/postgresql" \
        "$IMAGE_PATH" initdb -D /var/lib/postgresql/data >> "$LOG_FILE" 2>&1
    unset POSTGRES_PASSWORD
    if [[ $? -ne 0 ]]; then
        log "INIT" "PostgreSQL initialization failed. Check the log file for details."
        exit 1
    fi
else
    log "INIT" "PostgreSQL database already initialized. Skipping initialization."
fi

# Modify pg_hba.conf to allow connections from any host (FOR TESTING ONLY)
log "HBA" "Modifying pg_hba.conf"
apptainer exec \
    -B "${PGDATA_DIR}:/var/lib/postgresql/data" \
    -B "${RUN_DIR}:/var/run/postgresql" \
    "$IMAGE_PATH" sed -i '$ a\host all all 0.0.0.0/0 trust' /var/lib/postgresql/data/pg_hba.conf >> "$LOG_FILE" 2>&1

# Start the Apptainer instance
log "START" "Starting Apptainer instance..."
apptainer instance start \
    -B "${PGDATA_DIR}:/var/lib/postgresql/data" \
    -B "${RUN_DIR}:/var/run/postgresql" \
    "$IMAGE_PATH" "$INSTANCE_NAME" >> "$LOG_FILE" 2>&1 # Redirect output

# Start PostgreSQL inside the instance
log "START" "Starting PostgreSQL inside the instance..."
apptainer exec instance://"$INSTANCE_NAME" pg_ctl -D /var/lib/postgresql/data -l logfile start >> "$LOG_FILE" 2>&1

# Wait for PostgreSQL to become ready
log "CHECK" "Waiting for PostgreSQL to become ready..."
while ! apptainer exec instance://"$INSTANCE_NAME" pg_isready -h 127.0.0.1 -p 5432 -U postgres; do
    log "CHECK" "PostgreSQL is not yet ready. Retrying in 2 seconds..."
    sleep 2
done
log "CHECK" "PostgreSQL is ready."

# ***Create the haberc user and database***
log "USER" "Creating haberc user with password"
export PGPASSWORD="$PG_PASSWORD" # Use the correct password
apptainer exec instance://"$INSTANCE_NAME" psql -U postgres -c "CREATE USER $PG_USER WITH PASSWORD '$PG_PASSWORD';" >> "$LOG_FILE" 2>&1
unset PGPASSWORD

log "DATABASE" "Creating database"
export PGPASSWORD="$PG_PASSWORD"
apptainer exec instance://"$INSTANCE_NAME" createdb -O $PG_USER $PG_DATABASE >> "$LOG_FILE" 2>&1
unset PGPASSWORD

# Test the connection with the haberc user
log "TEST" "Testing the connection with haberc user"
export PGPASSWORD="$PG_PASSWORD" # Use the correct password
apptainer exec instance://"$INSTANCE_NAME" psql -U $PG_USER -d $PG_DATABASE -c '\q' >> "$LOG_FILE" 2>&1
unset PGPASSWORD

#Check postgresql status inside the container
apptainer exec instance://"$INSTANCE_NAME" pg_ctl -D /var/lib/postgresql/data status >> "$LOG_FILE" 2>&1
# Check the logfile inside the container
apptainer exec instance://"$INSTANCE_NAME" cat /var/lib/postgresql/data/logfile 2>/dev/null >> "$LOG_FILE" 2>&1

# Keep the job running
log "MAIN" "Postgresql is running in the background. Job will now sleep indefinitely. Stop the job to stop postgresql."
while true; do
    sleep 3600
done

# Stop the instance when the job is done (important!)
stop_postgres() {
    log "STOP" "Stopping PostgreSQL..."
    apptainer instance stop "$INSTANCE_NAME" >> "$LOG_FILE" 2>&1
    log "STOP" "PostgreSQL stopped."
}

trap stop_postgres SIGTERM EXIT
