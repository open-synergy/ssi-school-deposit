# Restart School Deposit Realization

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_realization`\
> **Menu:** School > School Deposit > Deposit Realizations\
> **Actor:** user in group `Validator`\
> **State:** `cancel` | `reject` → `draft`\
> **Requires:** `04-cancel`

## Pre-Condition

- **Record:** Status is **Cancelled** or **Rejected**.
- **Config:** An active `policy.template` grants `restart_ok` for that state to the
  actor's group.
- **Access:** User is in group `Validator`.

## Flow

1. Open the **School > School Deposit > Deposit Realizations** menu.
2. Open the record to restart.
3. Click the **Restart** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes back to **Draft**, shown on the statusbar.
