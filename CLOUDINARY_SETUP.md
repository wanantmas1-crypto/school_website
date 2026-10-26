# Cloudinary configuration

Django user uploads use Cloudinary only when Cloudinary credentials are
configured. Local development without credentials uses local filesystem media.
Static CSS, JavaScript, fonts, and application assets remain on the existing
WhiteNoise/static-files path.

## Credentials

Configure exactly one credential style in the deployment environment:

- `CLOUDINARY_URL`, or
- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and
  `CLOUDINARY_API_SECRET`.

Do not commit credentials or put API secrets in templates, JavaScript, logs,
or this guide. Use the deployment platform's secret manager. Rotate the
previously embedded API secret before deploying and update the replacement in
each service that still needs it.

## Transfer existing files

First export the media files from the verified live storage and confirm that
the files match database `FileField` references. The migration tool performs a
dry run unless `--apply` is supplied:

```powershell
python Busiada_Boarding\manage.py migrate_media_to_cloudinary `
  --source-dir 'D:\secure-export\media'
```

After setting the destination database, Cloudinary secrets, and
`DJANGO_DEBUG=False` in the process environment:

```powershell
python Busiada_Boarding\manage.py migrate_media_to_cloudinary `
  --source-dir 'D:\secure-export\media' --apply
```

The command verifies each uploaded object before changing its database file
name and never deletes the source file. It skips `Document.file` by default.
Use `--include-documents` only after verifying that the documents are intended
to be publicly accessible. Retain the original backup until every migrated
URL and its intended access policy have been checked.

## Admin uploads and access

The existing Django admin continues to use its model `FileField` controls.
Verify representative image, document, video, and audio uploads after
configuring Cloudinary. Public Cloudinary delivery is appropriate only for
content intended for public pages; do not migrate confidential or
authenticated-only records to public assets.
