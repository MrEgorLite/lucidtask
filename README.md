# lucidtask
For init db use tis command:
```
alembic upgrade head
```
To run project use this command:
```
gunicorn -k uvicorn.workers.UvicornWorker main:app
```