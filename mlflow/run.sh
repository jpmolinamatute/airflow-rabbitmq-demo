#!/usr/bin/env sh

mkdir -p "${USER_HOME}/mlruns"

if [ -z "$AWS_S3_BUCKET_NAME" ]; then
    echo "ERROR: AWS_S3_BUCKET_NAME is undefined" >&2
    exit 2
fi

if [ -z "$DB_URI" ]; then
    echo "ERROR: DB_URI is undefined" >&2
    exit 2
fi

exec /usr/local/bin/mlflow server \
    --host 0.0.0.0 \
    --file-store "${USER_HOME}/mlruns" \
    --default-artifact-root "s3://${AWS_S3_BUCKET_NAME}/mlruns" \
    --backend-store-uri "${DB_URI}"
