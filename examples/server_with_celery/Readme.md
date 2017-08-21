## Web Application that delegate tasks to remote workers

To run the example you need to:
### Step 1: Run celery workers
Make sure you have a celery compatible environment with celery package installed and a working rabbit mq or any other
message server.

```sh
cd server_with_celery
celery worker -A worker
```

### Step 2: Run web application

```sh
cd server_with_celery
python web.py
```