# Cloudinary Setup Guide for Busiada Boarding

## Step 1: Create Free Cloudinary Account

1. Go to https://cloudinary.com/users/register/free
2. Sign up with email (or GitHub)
3. Confirm your email
4. Log in to dashboard

## Step 2: Get Your Credentials

1. Go to **Dashboard** (https://cloudinary.com/console)
2. Look for **API Environment variable** section
3. Copy your **Cloud Name** (looks like: `abc123xyz`)
4. Click "Reveal" next to the API Key and API Secret
5. Copy all three:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

## Step 3: Install Package

```bash
pip install cloudinary
```

Add to `requirements.txt`:
```
cloudinary==1.40.0
```

## Step 4: Update Django Settings

In `Busiada_Boarding/config/settings.py`, add:

```python
import cloudinary
import cloudinary.storage
import os

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# Update Django storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'
```

## Step 5: Set Environment Variables

### For Local Development:
Create `.env` file in project root:
```
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here
```

Install `python-dotenv`:
```bash
pip install python-dotenv
```

In `Busiada_Boarding/config/settings.py` (top of file):
```python
from dotenv import load_dotenv
load_dotenv()
```

### For Render/Production:
1. Go to Render dashboard
2. Select your service
3. Go to **Environment**
4. Add the three variables

## Step 6: Test It Works

Run migrations:
```bash
python manage.py migrate
```

Upload a test image through Django admin and verify it appears on Cloudinary dashboard.

## Free Tier Limits
- 25GB storage/month
- 25GB bandwidth/month
- Great for school site

## Dashboard URL
Once set up, view all uploads: https://cloudinary.com/console/media_library

---

Need help? Let me know when you have your credentials and I'll update settings.py for you.
