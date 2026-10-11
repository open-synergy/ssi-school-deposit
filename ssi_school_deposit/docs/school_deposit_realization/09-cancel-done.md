# Cancel Done School Deposit Realization

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_realization`\
> **Menu:** School > School Deposit > Deposit Realizations\
> **Actor:** user in group `Validator`\
> **State:** `done` → `cancel`\
> **Requires:** `07-approve`

## Pre-Condition

- **Record:** Status is **Done**.
- **Config:** An active `policy.template` grants `cancel_ok` for state `done` to the
  actor's group.
- **Access:** User is in group `Validator`.

## Flow

1. Open the **School > School Deposit > Deposit Realizations** menu.
2. Open the record to cancel.
3. Click the **Cancel** button.
4. In the wizard that appears, select the **Cancellation Reason**.
5. Click **Confirm**.
6. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Cancelled**, shown on the statusbar.
- The reconciliations are removed and the journal entry is deleted.
- The deposit amount used becomes available again, and the invoice's unpaid amount is
  restored; a **Paid** invoice goes back to **Unpaid**.
- A payment that already settled the invoice is not moved.
