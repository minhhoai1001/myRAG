# API Server
## How to Migrate the Database with Alembic

1. **Create a new migration:**  
   ```bash
   alembic revision --autogenerate -m "Migration description"
   ```

2. **Apply migrations:**  
   ```bash
   alembic upgrade head
   ```

3. **(Optional) Revert to previous migration:**  
   ```bash
   alembic downgrade -1
   ```

> Make sure the `alembic.ini` configuration file points to your correct DATABASE_URL.

## Running the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```