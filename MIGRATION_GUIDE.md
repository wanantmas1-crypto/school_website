# Koyeb staging deployment

This runbook prepares the Django application for its first Koyeb deployment.
The first deployment should use a new, empty Supabase database. It will not
import the workspace SQLite database or any production content.

## Application preparation

- The Django WSGI application is `config.wsgi:application`.
- The repository-root `Dockerfile` builds the project, collects static files,
  and starts Gunicorn on Koyeb's supplied `PORT`.
- The container does not run database migrations during startup.
- `/healthz/` checks database connectivity and confirms that there are no
  unapplied Django migrations.
- WhiteNoise serves static assets; Cloudinary is used for uploaded media when
  configured.
- The previous Render deployment manifest has been removed. No hosting
  account, service, database, or Cloudinary asset has been changed by these
  local repository edits.

## 1. Create the empty staging database

Create a Supabase project for staging and obtain a PostgreSQL URL from its
dashboard. Use a direct connection if it is reachable from Koyeb; otherwise
use a Supabase session pooler. Do not use a transaction pooler without
validating driver compatibility.

The project settings require encrypted PostgreSQL connections. Keep the
connection URL in the Koyeb secret manager; do not commit it or paste it into
this repository.

Apply the schema to this empty database before starting the web service.
Either use an approved one-off command/job in your account, or run the
following from a trusted machine with the project dependencies installed.
Set these values only in that machine's temporary process environment:

```powershell
$env:DJANGO_DEBUG = 'False'
$env:DJANGO_REQUIRE_DATABASE_URL = 'True'
$env:DATABASE_URL = '<Supabase staging PostgreSQL URL>'
$env:DJANGO_SECRET_KEY = '<temporary secret>'
$env:DJANGO_ALLOWED_HOSTS = 'localhost,127.0.0.1'
$env:CSRF_TRUSTED_ORIGINS = 'https://localhost'
$env:CLOUDINARY_URL = '<rotated Cloudinary URL>'
python Busiada_Boarding\manage.py migrate --noinput
```

Do not store actual secret values in tracked files. The initial schema has no
school content; a Django administrator can be created once the database is
available using `python Busiada_Boarding\manage.py createsuperuser`.

## 2. Create the Koyeb web service

In Koyeb:

1. Connect the private GitHub repository `wanantmas1-crypto/school_website`
   and select the branch `migration/koyeb-supabase-cloudinary`.
2. Create a web service using the repository's root `Dockerfile`.
3. Expose the web service on HTTP port `8000`. The process binds to Koyeb's
   runtime-provided `PORT`.
4. Assign a Koyeb-generated `koyeb.app` hostname. Add that exact hostname to
   `DJANGO_ALLOWED_HOSTS` and add its `https://` origin to
   `CSRF_TRUSTED_ORIGINS`.
5. Configure an HTTP health check on `/healthz/`.
6. Set the runtime environment below in Koyeb. Use the secret manager for
   sensitive values.

| Variable | Value |
| --- | --- |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_REQUIRE_DATABASE_URL` | `True` |
| `DJANGO_SECRET_KEY` | A new, private Django secret |
| `DATABASE_URL` | The empty staging Supabase PostgreSQL URL |
| `DJANGO_ALLOWED_HOSTS` | The exact Koyeb hostname |
| `CSRF_TRUSTED_ORIGINS` | `https://` plus the exact Koyeb hostname |
| `CLOUDINARY_URL` | A rotated Cloudinary URL, or use all three individual credential variables instead |
| `CLOUDINARY_CLOUD_NAME` | Only if not using `CLOUDINARY_URL` |
| `CLOUDINARY_API_KEY` | Only if not using `CLOUDINARY_URL` |
| `CLOUDINARY_API_SECRET` | Only if not using `CLOUDINARY_URL` |

Configure either `CLOUDINARY_URL` or all three individual Cloudinary
credentials, not both. The Cloudinary API secret previously present in tracked
settings must be rotated before use; removing it from the current file does
not erase it from repository history.

HTTPS redirect, forwarded-protocol trust, and HSTS are deliberately not enabled
by default. Verify requests and redirects on the actual Koyeb domain before
opting into those settings.

## 3. Verify the staging site

After migrations are applied and Koyeb reports a healthy service:

- Confirm `/healthz/` returns HTTP 200 and the homepage loads.
- Verify static styles, scripts, fonts, navigation, and public routes.
- Create the initial administrator and test login/logout.
- Create temporary test content and verify the expected admin workflows.
- Upload a test public image to confirm Cloudinary storage and URL delivery.
- Verify the test upload remains accessible after redeployment.
- Check Koyeb logs for startup errors without exposing secret values.

This empty staging database does not contain the school's existing pages,
users, announcements, or media. Do not switch a public production domain to
this service until a separate, verified data-and-media migration is planned
and completed. Keep source backups and any existing site available until the
replacement is accepted.

## Work still requiring account access

The repository is prepared locally, but deployment requires:

- A Koyeb account authorized to access the private GitHub repository.
- A fresh Supabase staging project and its PostgreSQL URL.
- A Cloudinary account with a newly rotated API secret.
- A generated Django secret and the assigned Koyeb hostname.

Enter all secret values directly in Koyeb or the trusted command environment;
do not send them in chat. No staging database, Cloudinary account, or Koyeb
service has yet been created or deployed.
