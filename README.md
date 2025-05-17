# marrquee

You want a `.env` file like the following:

```
PLEX_BASE_URL=http://<ip>:32400
PLEX_TOKEN=my_plex_token
```

## Finding a plex token

* https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

## Debug

```
curl -i "http://localhost:1989/random-poster" \
  -H "Content-Type: application/json"

curl -i "http://localhost:1989/random-poster-redirect" \
  -H "Content-Type: application/json"

curl -i "http://localhost:1989/cache-poster" \
  -H "Content-Type: application/json"

curl -i "http://localhost:1989/random-cached-poster" \
  -H "Content-Type: application/json"

curl -i "http://localhost:1989/images?target=movies|custom|both" \
  -H "Content-Type: application/json"

curl -i "http://localhost:1989/images?target=movies" \
  -H "Content-Type: application/json"

curl -i "http://localhost:1989/images/{image_id}?target=..." \
  -H "Content-Type: application/json"

curl -i "http://localhost:1989/images/d1fbc6e060804688961a33a2e74da63a.jpg?target=movies" \
  -H "Content-Type: application/json"

curl -i "http://localhost:1989/random-image?target=movies" \
  -H "Content-Type: application/json"

curl -X POST http://localhost:1989/cache-custom-image \
  -H "Content-Type: application/json" \
  -d '{"url": "https://fastly.picsum.photos/id/418/200/200.jpg?hmac=FPLIYEnmfmXtqHPsuZvUzJeXJJbbxMWNq6Evh7mMSN4"}' --output output.jpg

curl -X POST "http://localhost:1989/cache/clear?target=movies" \
  -H "Content-Type: application/json"
```

## Run in Prod

```yaml
services:

  marrquee:
    container_name: marrquee
    image: ghcr.io/jzucker2/marrquee:latest
    restart: always
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - marrquee-storage:/data
    environment:
      - DEBUG=true
      - PLEX_BASE_URL=${PLEX_BASE_URL}
      - PLEX_TOKEN=${PLEX_TOKEN}
    ports:
      - "1989:1989"
    stdin_open: true
    tty: true

volumes:
  marrquee-storage:
```
