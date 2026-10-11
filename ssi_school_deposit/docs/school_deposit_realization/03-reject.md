# Reject School Deposit Realization

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_realization`\
> **Menu:** School > School Deposit > Deposit Realizations\
> **Actor:** approver on the pending approval level\
> **State:** `confirm` → `reject`\
> **Requires:** `02-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**.
- **Config:** An active `policy.template` grants `reject_ok` to the actor's group.
- **Access:** User is registered as an approver on the approval level that is currently
  **pending**.

## Flow

1. Open the **School > School Deposit > Deposit Realizations** menu.
2. Open the record to reject.
3. Click the **Reject** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Rejected**, shown on the statusbar.
- The document can be brought back to **Draft** via **Restart** -- see `05-restart`.
