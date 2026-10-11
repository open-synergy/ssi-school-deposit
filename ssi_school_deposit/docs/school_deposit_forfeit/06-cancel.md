# Cancel School Deposit Forfeit

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_forfeit`\
> **Menu:** School > School Deposit > Deposit Forfeits\
> **Actor:** user in group `Validator`\
> **State:** `draft` | `confirm` | `done` → `cancel`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**, **Waiting for Approval**, or **Done**.
- **Config:** An active `policy.template` grants `cancel_ok` for that state to the
  actor's group.
- **Access:** User is in group `Validator`.

## Flow

1. Open the **School > School Deposit > Deposit Forfeits** menu.
2. Open the record to cancel.
3. Click the **Cancel** button.
4. In the wizard that appears, select the **Cancellation Reason**.
5. Click **Confirm**.
6. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Cancelled**, shown on the statusbar.
- For a **Done** document, the reconciliations are removed and the journal entry is
  deleted, so the forfeited deposit becomes available again.
