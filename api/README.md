# API Server

## Running the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## MinIO Setup

After starting MinIO, you need to configure the bucket and CORS for direct browser uploads.

### Option 1: Using Python Script (Recommended)

```bash
cd api
python -m app.services.setup_minio
```

### Option 2: Using MinIO Console

1. Access MinIO Console at http://localhost:9001
2. Login with your credentials (default: minioadmin/minioadmin)
3. Create bucket if it doesn't exist (default: "documents")
4. Go to Bucket > Manage > Access Rules
5. Add CORS rule:
   - Allowed Origins: `*` (or your webui URL for production)
   - Allowed Methods: `GET, PUT, POST, DELETE, HEAD`
   - Allowed Headers: `*`
   - Max Age: `3000`

### Environment Variables

The API supports both naming conventions:
- `MINIO_ENDPOINT_URL` or `AWS_ENDPOINT_URL`
- `S3_BUCKET` or `AWS_BUCKET`

## Troubleshooting Upload Issues

If document uploads fail:

1. **Check environment variables**: Ensure `AWS_ENDPOINT_URL` (or `MINIO_ENDPOINT_URL`) and `AWS_BUCKET` (or `S3_BUCKET`) are set correctly
2. **Check CORS**: Run the setup script or configure CORS in MinIO console
3. **Check bucket exists**: The setup script will create it automatically
4. **Check network**: Ensure MinIO is accessible from both API and browser
5. **Check browser console**: Look for CORS errors or network errors

Common errors:
- **CORS error**: MinIO CORS not configured - run setup script
- **403 Forbidden**: Bucket permissions issue - check MinIO access policy
- **Connection refused**: MinIO not running or wrong endpoint URL