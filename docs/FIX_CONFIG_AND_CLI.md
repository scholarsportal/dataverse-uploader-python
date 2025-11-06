# Fix for Configuration and Environment Variable Issues

## Problems Fixed

1. ✅ Pydantic validation error with `dataset_pid` alias
2. ✅ Environment variables not being loaded from `.env` file
3. ✅ Options marked as required even when env vars are set

## Download Fixed Files

- [cli_fixed_v2.py](computer:///mnt/user-data/outputs/cli_fixed_v2.py) - Fixed CLI
- [config_fixed.py](computer:///mnt/user-data/outputs/config_fixed.py) - Fixed config

## Quick Fix Steps

```powershell
cd C:\Users\PCUSER\Downloads\dataverse_uploader_python

# Replace both files
Copy-Item cli_fixed_v2.py dataverse_uploader\cli.py
Copy-Item config_fixed.py dataverse_uploader\core\config.py

# Reinstall
poetry install
```

## Verify Your .env File

Make sure your `.env` file exists in the project root and contains:

```env
DV_SERVER_URL=https://demo.borealisdata.ca
DV_API_KEY=a0359724-f3cd-44c7-9864-49575f3cf1da
DV_DATASET_PID=doi:10.80240/FK2/SKB8TV
```

**Important:** 
- The `.env` file should be in the same directory as `pyproject.toml`
- No `/api` suffix on the server URL (the uploader adds it)
- No quotes around values
- No spaces around `=`

## Create .env File (if needed)

```powershell
@"
DV_SERVER_URL=https://demo.borealisdata.ca
DV_API_KEY=a0359724-f3cd-44c7-9864-49575f3cf1da
DV_DATASET_PID=doi:10.80240/FK2/SKB8TV
"@ | Out-File -FilePath .env -Encoding UTF8
```

## Test It Works

### With .env file (preferred):

```powershell
# Create a test file
"id,name,value`n1,test,100" | Out-File test.csv

# Should work now without command-line arguments!
dv-upload test.csv --list-only
```

### With command-line arguments:

```powershell
dv-upload test.csv `
  -s https://demo.borealisdata.ca `
  -k a0359724-f3cd-44c7-9864-49575f3cf1da `
  -d doi:10.80240/FK2/SKB8TV `
  --list-only
```

## What Was Changed

### config.py Changes:
1. Added `extra="ignore"` to model config (allows extra fields)
2. Added `populate_by_name=True` (supports both field names and aliases)
3. Removed problematic alias from `dataset_pid` field

### cli.py Changes:
1. Added `from dotenv import load_dotenv` import
2. Added `load_dotenv()` call at module level
3. Changed required options to optional (uses env vars as fallback)
4. All three main options (server, api_key, dataset) now default to `None`

## Expected Output

After the fix, running:
```powershell
dv-upload test.csv --list-only
```

Should show:
```
Dataverse Uploader v1.3.0
Server: https://demo.borealisdata.ca
Dataset: doi:10.80240/FK2/SKB8TV

LIST ONLY MODE - No files will be uploaded
...
```

## Troubleshooting

### Still getting "Missing option" error:

```powershell
# Make sure .env is in the right place
Test-Path .env

# Check the contents
Get-Content .env

# Reinstall with cache clear
poetry install --no-cache
```

### Still getting validation errors:

```powershell
# Delete old build artifacts
Remove-Item -Recurse -Force dataverse_uploader\__pycache__
Remove-Item -Recurse -Force dataverse_uploader\core\__pycache__

# Reinstall
poetry install
```

### Can't find .env file:

```powershell
# Show where you are
Get-Location

# List files to confirm .env exists
Get-ChildItem -Name

# .env should be in the same directory as pyproject.toml
```

## After Fix - Your Commands Will Work!

### Simple command (uses .env):
```powershell
dv-upload test.csv --list-only
```

### With directory:
```powershell
dv-upload data/ --list-only --recurse
```

### Override .env values:
```powershell
dv-upload test.csv -s https://other-server.org --list-only
```

All of these should work now! 🎉
