# Points of Confusion

Documenting unclear areas and unresolved questions.

---

## SDK and Connection

- Why did Begin Session fail with error -2147220472?
  - Answer: QuickBooks was not open or no company file loaded

- Do I need to be added as a QuickBooks user?
  - Answer: No. SDK authenticates at application level, not user level

- What is the difference between Open Connection and Begin Session?
  - Open Connection: Connects to the SDK/QuickBooks application
  - Begin Session: Opens a session with a specific company file

- Can I develop without access to their machine?
  - Unclear. Options: trial + sample company, or get backup file

---

## Environment Setup

- How do I test without affecting their real data?
  - No official sandbox for QuickBooks Desktop
  - Must use: trial version, sample company, or backup file

- Do I need QuickBooks installed on my machine to develop?
  - Yes, if using SDK directly
  - Alternative: Conductor (REST API) may not require local QB

- Can I develop on Mac?
  - No. QuickBooks Desktop SDK is Windows only
  - Need Windows machine or VM

---

## API and Integration Options

- Which API should I use?
  - Not decided yet. See RESEARCH-OPTIONS.md

- What is qbXML?
  - XML format specific to QuickBooks SDK
  - Used for all requests and responses

- Why does QuickBooks use XML instead of JSON?
  - Legacy system built in 2000s
  - No modern REST API for Desktop version

- What is the difference between SDK, Web Connector, and Conductor?
  - SDK: Direct local connection, qbXML, free
  - Web Connector: Web service bridge, still qbXML, free
  - Conductor: Third-party REST wrapper, JSON, paid

---

## Third-Party Tools

- Does Coefficient work with QuickBooks Desktop Enterprise?
  - Unknown. Must verify.

- Does Apix Drive work with QuickBooks Desktop Enterprise?
  - Unknown. Must verify.

- Does FinJinni work with QuickBooks Desktop Enterprise?
  - Unknown. Must verify.

- Which third-party tool is best?
  - Not decided. Depends on budget, coding ability, automation needs

---

## Development Process

- What do I build first?
  - Unclear. Need to confirm connection works before coding

- What language should I use?
  - Options: Node.js, C#, VB.NET
  - No decision made yet

- Where does the packing slip Excel file come from?
  - Unknown. Need to clarify: local folder, email, cloud storage?

- How does the automation trigger?
  - Unknown. Options: manual run, file watcher, scheduled task

---

## Business Logic

- Where does the RATE/price come from for invoices?
  - Unknown. From QB item? Separate lookup? Manual input?

- Are all customers already in QuickBooks?
  - Unknown. If not, need to create them first

- Are all items (IPHONE 12, etc.) already in QuickBooks?
  - Unknown. If not, need to create them first

- What happens if an IMEI already exists?
  - Unknown. Error handling not defined

- What template fields are required vs optional?
  - Need to inspect "INVOICE R2 FULLY FUNCTIONAL" template

---

## Access and Permissions

- Who at the company can authorize SDK access?
  - Unknown. Need to identify person with Admin rights

- Can I get remote access to their machine?
  - Unknown. Need to request

- Can they send me a backup file to test locally?
  - Unknown. Need to ask

---

there is no confusion on my end
i act as a word of God.
i act as a word of God.

## Unresolved Decisions

- [ ] Which integration approach to use (SDK, QBWC, Conductor, other)
- [ ] Local development vs remote development
- [ ] Test environment setup method
- [ ] Programming language choice
- [ ] Automation trigger mechanism
- [ ] Error handling strategy

---

## Questions to Ask the Company

1. Can I get remote access to the QuickBooks machine?
2. Can you send a backup file for local testing?
3. Who has Admin rights to authorize the SDK app?
4. Are all customers and items already in QuickBooks?
5. Where do packing slip Excel files get saved?
6. How should pricing/rates be determined?
