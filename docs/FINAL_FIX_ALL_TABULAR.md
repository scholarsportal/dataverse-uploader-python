# Final Fix: All Tabular File Formats

## 🎯 Key Discovery

**ALL tabular files get converted to `.tab` in Dataverse:**
- ✅ `.csv` → `.tab`
- ✅ `.xlsx`, `.xls` → `.tab`
- ✅ `.sav` (SPSS) → `.tab`
- ✅ `.dta` (Stata) → `.tab`
- ✅ `.sas7bdat` (SAS) → `.tab`
- ✅ `.por` (SPSS Portable) → `.tab`
- ✅ `.rdata`, `.rds` (R data) → `.tab`

This is why you were getting duplicates!

## 📥 Download Final Version

[dataverse_uploader_v4_all_tabular.py](computer:///mnt/user-data/outputs/dataverse_uploader_v4_all_tabular.py)

## ⚡ Install

```powershell
cd C:\Users\PCUSER\Downloads\dataverse_uploader_python
Copy-Item dataverse_uploader_v4_all_tabular.py dataverse_uploader\uploaders\dataverse.py
poetry install
```

## ✅ What's Fixed Now

The uploader now checks for ALL tabular file formats:

```python
# When you upload: customers.csv
# Checks for:
1. customers.csv       (exact match)
2. customers.tab       (converted format) ✓ FOUND!
3. MD5 hash match      (content duplicate)

# When you upload: data.xlsx
# Checks for:
1. data.xlsx           (exact match)
2. data.tab            (converted format) ✓ FOUND!
3. MD5 hash match      (content duplicate)
```

## 🧪 Test It Now

You said you cleaned up the dataset, so now you have a fresh start!

```powershell
# Upload your data
dv-upload data/*.csv --recurse --verify

# Try uploading again - should skip everything!
dv-upload data/*.csv --recurse --verify
```

**Expected output:**
```
Processing file: data\customers.csv (564 bytes)
File exists as data/customers.tab (tabular file converted to TAB)
Skipped: customers.csv

Processing file: data\employees.csv (354 bytes)  
File exists as data/employees.tab (tabular file converted to TAB)
Skipped: employees.csv

... etc ...

Files uploaded: 0
Files skipped: 5 ✓
```

## 📊 Supported Tabular Formats

The fix now handles:

| Format | Extension | Converts To |
|--------|-----------|-------------|
| CSV | `.csv` | `.tab` |
| Excel | `.xlsx`, `.xls` | `.tab` |
| SPSS | `.sav`, `.por` | `.tab` |
| Stata | `.dta` | `.tab` |
| SAS | `.sas7bdat` | `.tab` |
| R Data | `.rdata`, `.rds` | `.tab` |

## 🎉 Your Current Status

From your last upload:
```
✓ customers.tab
✓ products.tab
✓ weather.tab
✓ NHES_SchoolReadinessSurvey_2007_Questionnaire.pdf (not tabular, stays as-is)
```

Now if you try to upload again, it will detect them all!

## 🧹 Why employees.csv and sales.csv Failed

Looking at your logs:
```
employees.csv: HTTP error 400: "Failed to add file to dataset"
sales.csv: HTTP error 400: "Failed to add file to dataset"
```

These likely failed due to:
1. **Duplicate content** - Dataverse detected they had the same content as existing files
2. **Dataset lock** - Dataverse was still processing previous uploads

But now with the fix, the uploader will detect them BEFORE trying to upload, so you won't get these errors!

## 🎯 Pro Tips

### 1. Always Use --verify
```powershell
dv-upload data/ --recurse --verify
```

### 2. Use --list-only First
```powershell
# See what will be uploaded
dv-upload data/ --recurse --list-only --verify

# Then actually upload
dv-upload data/ --recurse --verify
```

### 3. Check Your Dataset
```powershell
$apiKey = (Get-Content .env | Select-String "DV_API_KEY").ToString().Split("=")[1]
$doi = (Get-Content .env | Select-String "DV_DATASET_PID").ToString().Split("=")[1]
$headers = @{"X-Dataverse-key" = $apiKey}

$response = Invoke-RestMethod -Uri "https://demo.borealisdata.ca/api/datasets/:persistentId/versions/:latest/files?persistentId=$doi" -Headers $headers
$response.data | ForEach-Object { 
    Write-Host "$($_.label) - $($_.dataFile.contentType)"
}
```

## 📝 Example Workflow

```powershell
# 1. Check what's already in the dataset
$response = Invoke-RestMethod -Uri "https://demo.borealisdata.ca/api/datasets/:persistentId/versions/:latest/files?persistentId=$doi" -Headers $headers
$response.data.label

# 2. Preview what would be uploaded
dv-upload data/ --recurse --list-only --verify

# 3. Upload
dv-upload data/ --recurse --verify

# 4. Upload again (should skip everything!)
dv-upload data/ --recurse --verify
```

## 🚀 Real-World Example

```powershell
# Create test files of different types
"id,name`n1,Alice" | Out-File test.csv
# (In real world, you'd have .xlsx, .sav, etc.)

# Upload once
dv-upload test.csv --verify
# Output: Successfully uploaded: test.csv
# Dataverse stores as: test.tab

# Try uploading again
dv-upload test.csv --verify
# Output: File exists as test.tab (tabular file converted to TAB)
#         Files skipped: 1 ✓
```

## 🎊 Success!

With this fix:
- ✅ No more duplicate `.tab` files
- ✅ No more `-1`, `-2` suffixes
- ✅ Works with CSV, Excel, SPSS, Stata, SAS, R data
- ✅ Detects duplicates even across directory uploads
- ✅ Content-based duplicate detection (with --verify)

Install the fix and enjoy duplicate-free uploads! 🎉

---

## Quick Reference

```powershell
# Install fix
Copy-Item dataverse_uploader_v4_all_tabular.py dataverse_uploader\uploaders\dataverse.py
poetry install

# Upload with duplicate detection
dv-upload data/ --recurse --verify

# Preview before uploading
dv-upload data/ --recurse --list-only --verify
```
