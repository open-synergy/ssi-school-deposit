# Reject School Deposit Forfeit

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_forfeit`\
> **Menu:** School > School Deposit > Deposit Forfeits\
> **Actor:** approver on the pending approval level\
> **State:** `confirm` → `reject`\
> **Requires:** `03-confirm`

## Pre-Condition

- **Record:** Status is **Waiting for Approval**.
- **Config:** An active `policy.template` grants `reject_ok` to the actor's group.
- **Access:** User is registered as an approver on the approval level that is currently
  **pending**.

## Flow

1. Open the **School > School Deposit > Deposit Forfeits** menu.
2. Open the record to reject.
3. Click the **Reject** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Rejected**, shown on the statusbar.
- The deposit is untouched; no journal entry exists.
