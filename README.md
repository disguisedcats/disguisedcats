# disguisedcats

## backend

### Run locally

#### Preparation

Before running the whole application, database setup is required. This is a one-time
thing, you can skip it if you've already done it.

First, run the database.

```bash
docker compose --profile dev up -d db
```

Then, start a `mongosh` session in the running container with the default admin credentials
(default credentials could be overriden in the `docker-compose.yml` or by adding an `override.env` file).

```bash
docker compose exec db mongosh -u admin -p verysecretadminpass admin
```

In the executed `mongosh` session run the script from [`scripts/init-mongo.js`](./scripts/init-mongo.js)
to create a new user for the backend application. You can change the credentials listed in the script,
but don't forget to update them in the `app` service in `docker-compose.yml` or using an `override.env` file.

To exit the `mongosh` session run the `exit` command.

#### Running

Add `127.0.0.1 example.localhost` line to end of the `/etc/hosts` file.
This is required because the backend  relies on the requests' hostname to properly function.

Run services with docker compose:

```
docker compose --profile dev up -d
```

Open `http://example.localhost` in your browser.

#### Adding subdomains

The backend generated apps and expects requests for them from third-level domains.
Therefore, after creating an app, you'll be presented with a link to it, but it won't
open in a browser because in the `/etc/hosts` we've added only the second-level domain
`example.localhost`.

To be able to open the third-level domain, you have to add it to `/etc/hosts` manually
the same way as the second-level one: `127.0.0.1 generated-domain.example.localhost`.
