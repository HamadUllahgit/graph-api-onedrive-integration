# Azure App Registration Setup Guide

Step-by-step guide for creating an Azure App Registration with Microsoft Graph API access to OneDrive.

## Prerequisites

- Azure AD Global Administrator or Application Administrator role
- Access to Azure Portal (portal.azure.com)

## Step 1: Register the Application

1. Go to [portal.azure.com](https://portal.azure.com)
2. Search for **"App registrations"** in the top search bar
3. Click **+ New registration**
4. Fill in:
   - **Name:** `OneDrive API Reader` (or descriptive name)
   - **Supported account types:** `Accounts in this organizational directory only`
   - **Redirect URI:** Leave blank (not needed for client credentials)
5. Click **Register**

## Step 2: Copy Application & Tenant IDs

After registration, you'll see the app overview page.

Copy these values and save them securely:

| Value | Location |
|-------|----------|
| Application (client) ID | Overview page |
| Directory (tenant) ID | Overview page |

## Step 3: Create Client Secret

1. In the left sidebar, click **Certificates & secrets**
2. Click **+ New client secret**
3. Enter:
   - **Description:** `Production` (or environment name)
   - **Expires:** 12 months or 24 months (recommended)
4. Click **Add**

⚠️ **CRITICAL:** Copy the **Value** immediately after creation. It only shows once!

Do NOT copy the "Secret ID" - you need the "Value" column.

## Step 4: Add API Permissions

1. In the left sidebar, click **API permissions**
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Select **Application permissions** (NOT Delegated)
5. Search and check:
   - `Files.Read.All` (under Files)
   - `User.Read.All` (under User)
6. Click **Add permissions**

## Step 5: Grant Admin Consent

Still on the API permissions page:

1. Click **Grant admin consent for [your tenant]**
2. Click **Yes** to confirm

You should see green checkmarks ✅ next to both permissions.

## Summary - Your Credentials

After completing these steps, you'll have:

```
TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
USER_EMAIL=user@yourtenant.onmicrosoft.com
```

## Security Checklist

- [ ] Credentials stored in secure location (not in code)
- [ ] Client secret expiry date noted in calendar
- [ ] Read-only permissions confirmed
- [ ] Single tenant only (not multi-tenant)
- [ ] Admin consent granted

## Troubleshooting

### "Insufficient privileges" error

- Admin consent not granted
- Solution: Complete Step 5

### "Invalid client secret" error

- Secret copied incorrectly (copied ID instead of Value)
- Secret has expired
- Solution: Create new secret, copy Value

### "User not found" error

- User email incorrect
- User not licensed for OneDrive
- Solution: Verify email in Azure AD → Users
