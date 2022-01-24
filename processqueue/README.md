# processqueue

## Application for development

### Build

```shell
docker build -t processqueue .
```

### Run

```shell
docker run -p 8080:8080 processqueue
```

## Application for production (without test dependencies)

### Build

```shell
docker build -t processqueue-production --build-arg APP_ENV=production .
```

### Run

```shell
docker run -p 8080:8080 processqueue-production
```

## Tests

### Build

```shell
docker build -t processqueue-test --target=test .
```

### Run

```shell
docker run processqueue-test
```
