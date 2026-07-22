# Scripts

Utility and automation scripts for the vk-lip project.

## Tax Delinquency Import

Load a delinquency report into the `parcels` table with:

```bash
cd /workspaces/vk-lip/backend
/workspaces/vk-lip/.venv/bin/python -m app.imports.import_tax_delinquency /workspaces/vk-lip/data/raw/Report_RE_DelinquentAccIndex_07012026.csv
```

Notes:

- The importer updates `Parcel.tax_delinquent` and `Parcel.tax_lien_amount` as a full snapshot.
- Report-style CSV files with preamble rows are supported as long as they expose a parcel key such as `parcel_number`, `ParcelNumber`, `Parcel ID`, `APN`, or `PIN #`.
- `Report_RE_DelinquentAccIndex_07012026.csv` is supported and imports delinquency flags correctly.
- `Delinquent_Accounts_Report_WithCunumber_07012026.csv` is not imported by default because it is an account-level report with `CuNumber` and bill-address data, not a deterministic parcel identifier stored in the current schema.
