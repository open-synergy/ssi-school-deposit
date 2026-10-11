# Approve School Deposit Forfeit

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_forfeit`\
> **Menu:** School > School Deposit > Deposit Forfeits\
> **Actor:** approver of the approval level\
> **State:** `confirm` → `done`\
> **Requires:** `03-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**.
- **Data:** The document has lines, and no line takes more than its source journal item
  still holds.
- **Config:** The Type has a **Forfeit Account**, and the document has a **Journal**.
- **Config:** An active `policy.template` grants `approve_ok` for state `confirm`; the
  actor is an active approver of the document.
- **Access:** User is the active approver.

## Flow

1. Open the **School > School Deposit > Deposit Forfeits** menu.
2. Open the record to approve.
3. Click the **Approve** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Done**, shown on the statusbar, when every approval level is
  fulfilled.
- A document number is assigned.
- A journal entry is posted: a credit on the Forfeit Account and a debit on the Deposit
  Account per line. Each debit is reconciled with its deposit journal item, so the
  remaining deposit of each item is reduced by the line's Amount.
- Finishing is rejected with an error when the Forfeit Account or Journal is empty, when
  there are no lines, or when a line exceeds what its source item still holds.
