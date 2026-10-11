# Approve School Deposit Realization

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_realization`\
> **Menu:** School > School Deposit > Deposit Realizations\
> **Actor:** approver of the approval level\
> **State:** `confirm` → `done`\
> **Requires:** `02-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**.
- **Data:** The document has lines, and its **Amount Total** does not exceed what the
  invoice may be settled with, nor what each source journal item still holds.
- **Config:** An active `policy.template` grants `approve_ok` for state `confirm`; the
  actor is an active approver of the document.
- **Access:** User is the active approver.

## Flow

1. Open the **School > School Deposit > Deposit Realizations** menu.
2. Open the record to approve.
3. Click the **Approve** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Done**, shown on the statusbar, when every approval level is
  fulfilled.
- A document number is assigned.
- A journal entry is posted: a credit on the receivable account of the invoice and a
  debit on the Deposit Account per line. It is reconciled with the invoice and with the
  deposit journal items, so the invoice's unpaid amount and the remaining deposit are
  both reduced by **Amount Total**.
- Finishing is rejected with an error when a total or a line exceeds what is allowed.
