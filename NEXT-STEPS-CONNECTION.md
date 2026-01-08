# QuickBooks Connection Setup — Next Steps

## Goal
Establish a working SDK connection to QuickBooks before writing any automation code.

---

## Prerequisites

- Windows machine
- QuickBooks Enterprise installed
- QuickBooks SDK installed (you have this — SDKTestPlus3 works)

---

## Step 1: Get Access to a Company File

Choose one path:

### Path A: Use Company's Real Environment
1. Request remote desktop access to the machine running QuickBooks
2. Coordinate with someone who has QuickBooks Admin rights
3. They must be present (or you need their login) to authorize the app first time

### Path B: Test Locally with Trial
1. Download QuickBooks Desktop Enterprise trial: https://quickbooks.intuit.com/desktop/enterprise/free-trial/
2. Install on your Windows machine
3. Create a sample company (File > New Company > Create a sample company)
4. Use this for all development and testing

### Path C: Get a Backup File
1. Ask the company for a backup (.qbb or .qbw file)
2. Restore it in your local QuickBooks installation
3. Test against real data structure without affecting production

---

## Step 2: Verify QuickBooks is Running

1. Open QuickBooks Desktop
2. Open a company file (File > Open or Restore Company)
3. Confirm you see the home screen with the company loaded
4. Leave QuickBooks open — do not close it

---

## Step 3: Test SDK Connection

1. Open SDKTestPlus3
2. Click **Open Connection**
   - Expected: "Open Connection call successful"
3. Click **Begin Session**
   - First time: QuickBooks will show an authorization dialog
   - Select "Yes, always allow access" and check "Allow this application to access personal data"
   - Click Continue
4. Expected result: "Begin Session call successful"

If Begin Session fails:
- Confirm QuickBooks is open with a company file
- Confirm you are on the same machine (not remote unless configured)
- Check QuickBooks is not showing any modal dialogs

---

## Step 4: Test a Simple Query

In SDKTestPlus3:

1. Go to the Request tab
2. Select **CustomerQueryRq** from the dropdown
3. Click **Add to Message**
4. Click **Send Request**
5. Check Response tab — you should see XML with customer data

If this works, the connection is confirmed.

---

## Step 5: Test Invoice Creation (Read-Only First)

Before creating invoices, query existing ones:

1. In SDKTestPlus3, select **InvoiceQueryRq**
2. Click **Add to Message**
3. Click **Send Request**
4. Review the XML response — note the structure and fields

This shows you what invoice data looks like in qbXML.

---

## Step 6: Authorization Levels

When QuickBooks asks to authorize the app, there are permission levels:

| Level | Access |
|-------|--------|
| No | Deny access |
| Yes, prompt each time | Ask every session |
| Yes, always | Allow without prompts |

For development, select **Yes, always** to avoid repeated prompts.

To manage authorized apps later:
- QuickBooks > Edit > Preferences > Integrated Applications > Company Preferences

---

## After Connection is Confirmed

Once Step 4 works (query returns data):

1. Connection is verified
2. You can begin developing automation code
3. Start with read operations (queries) before write operations (creates)
4. Test invoice creation on sample/test company first

---

## If You Cannot Access Their QuickBooks

Options:
1. Install trial and build against sample company — deploy to their environment later
2. Have them run SDKTestPlus3 on their end and send you screenshots of the XML structure
3. Use Conductor (REST API) which may simplify remote development

---

## Summary Checklist

- [ ] QuickBooks installed
- [ ] Company file accessible
- [ ] SDKTestPlus3 Open Connection successful
- [ ] SDKTestPlus3 Begin Session successful
- [ ] Authorization granted in QuickBooks
- [ ] CustomerQueryRq returns data
- [ ] Ready to develop

---

## Contact Points

If testing on company environment, get:
- Remote access credentials
- Name of person with QuickBooks Admin rights
- Scheduled time when they can authorize the app
