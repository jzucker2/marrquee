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
curl -i "http://localhost:8000/random-poster" \
-H "Content-Type: application/json"

curl -i "http://localhost:8000/random-poster-redirect" \
-H "Content-Type: application/json"

curl -i "http://localhost:8000/cache-poster" \
-H "Content-Type: application/json"

curl -i "http://localhost:8000/random-cached-poster" \
-H "Content-Type: application/json"
```
