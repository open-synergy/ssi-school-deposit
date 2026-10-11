# Confirm School Deposit Realization

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_realization`\
> **Menu:** School > School Deposit > Deposit Realizations\
> **Actor:** user in group `User`\
> **State:** `draft` → `confirm`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**.
- **Config:** An active `policy.template` for this model grants `confirm_ok` for state
  `draft` to the actor's group.
- **Config:** An active `approval.template` for this model matches this record and has
  at least one approver level.
- **Config:** An active `sequence.template` exists for this model.
- **Access:** User is in group `User`.

## Flow

1. Open the **School > School Deposit > Deposit Realizations** menu.
2. Open the record to confirm.
3. Click the **Confirm** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- Status changes to **Waiting for Approval**, shown on the statusbar.
- Approval records are created for each approver level defined by the approval template.
