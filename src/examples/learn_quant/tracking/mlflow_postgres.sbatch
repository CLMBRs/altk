#!/bin/bash
#SBATCH --job-name=mlflow_postgres
#SBATCH --output=mlflow_postgres.out
#SBATCH --error=mlflow_postgres.err
#SBATCH --time=4-00 # Adjust as needed
#SBATCH --requeue
#SBATCH --partition=gpu-l40 # Replace with your partition
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --nodelist=g3116
#SBATCH --cpus-per-task=4 # Adjust based on your needs

source ~/.bashrc
conda activate altk

export NODE_IP=$(hostname -i)
echo "Node IP Address: $NODE_IP"

# Load environment variables from .env file
if [ -f .env_mlflow ]; then
    export $(grep -v '^#' .env_mlflow | xargs)
else
    echo "ERROR: .env_mlflow file not found. Please create one with the necessary environment variables."
    exit 1
fi

export MLFLOW_TRACKING_URI="postgresql+psycopg2://${PG_USER}:${PG_PASSWORD}@${PG_HOST}:${PG_PORT}/${PG_DATABASE}"
export MLFLOW_SERVER_PORT=5000

echo $MLFLOW_TRACKING_URI

# Function to check if the port is in use

is_port_in_use() {
    netstat -tulnp | grep ":$1 " > /dev/null
    return $? # Returns 0 if port is in use, 1 otherwise
}

# Start MLflow server in the foreground
mlflow server \
    --backend-store-uri "$MLFLOW_TRACKING_URI" \
    --host 0.0.0.0 \
    --port "$MLFLOW_SERVER_PORT" \
    --gunicorn-opts "--worker-class gevent --threads 3 --workers 3 --timeout 300 --keep-alive 300 --log-level INFO"

# Check if the server started successfully by checking if the port is open
if ! is_port_in_use "$MLFLOW_SERVER_PORT"; then
    echo "ERROR: MLflow server failed to start. Check mlflow_server.log and mlflow_server.err"
    exit 1 # Exit with error code to trigger requeue
fi

echo "MLflow server started successfully on port $MLFLOW_SERVER_PORT"

# The script will now stay in the foreground. When the time limit is reached, Slurm will kill the job, including the mlflow server, and because of --requeue, it will restart the job