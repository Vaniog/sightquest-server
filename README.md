# SightQuest Server

![image](https://github.com/Vaniog/sightquest-server/assets/79862574/93f5e3b5-bfc4-458c-81f1-7870259da5f6)

[Project Site](https://sightquest.ru)


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
