
# Dagster Celery Example

All required services are started as docker container. A custom image serves as worker image 
and as test image for manual interactions.

## Infrastructure

- RabbitMQ is used as message queue to pass Celery tasks and status messages. 
- Postgres is used as Celery result store and Dagster DB. 
- Minio is used as intermediate store for Dagster.

```bash
docker-compose up rabbit postgres minio
```


## Workers

Runs two workers, a generic one and a (fake-) GPU-accelerated one.

```bash
docker-compose up worker-generic 
docker-compose up worker-gpu 
```



## Dagit

Run a Dagit instance where tasks can be triggered manually through the Dagit UI.

```bash
docker-compose up dagit
```

- Point your browser at http://localhost:3000
- Go to Playground
- Use the following config as example:

```yaml
solids: 
  basic_solid:
    inputs:
      in1: one, two, test!
execution:
  celery:
    config:
      broker: pyamqp://rabbit:rabbit@rabbit:5672//
      backend: db+postgresql://postgres:postgres@postgres:5432/dagster_celery
intermediate_storage:
  s3:
    config:
      s3_bucket: dagster-intermediates
resources:
  s3:
    config:
      endpoint_url: http://minio:9000/
      access_key: minio
      secret_key: miniosecret
```
