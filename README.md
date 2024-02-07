# SightQuest Server

## How to start

To start app:

```
git clone https://github.com/shampiniony/sightquest-server.git
git checkout dev
cd backend
```

### Dev version

Then you have to fill `.env` file using `.env.example` (Yandex.cloud credentials needed) or change models: User, GamePhoto.

```
docker-compose up --build -d
```

### Prod version

Then you have to fill `.env` file using `.env.prod.example` (Yandex.cloud credentials needed) or change models: User, GamePhoto.

```
docker-compose up -f docker-compose.prod.yml --build -d
```
