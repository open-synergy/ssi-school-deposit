# Compute Lines of School Deposit Forfeit

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_forfeit`\
> **Menu:** School > School Deposit > Deposit Forfeits\
> **Actor:** user in group `User`\
> **State:** `draft`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**, with **Type** and **Partner** filled in.
- **Data:** The Partner has an unused deposit: a posted customer invoice line of a
  Deposit Product of the Type whose credit on the Deposit Account is not yet reconciled.
- **Access:** User is in group `User`.

## Flow

1. Open the **School > School Deposit > Deposit Forfeits** menu.
2. Open the record to compute.
3. Click the **Compute Lines** button.

## Post-Condition

- The **Lines** tab lists one line per unused deposit journal item of the Partner,
  oldest first, each for the whole amount the item still has.
- A deposit already used by a realization is counted only for what is left of it.
- Lines entered earlier are replaced. **Amount Total** equals the sum of the lines.
- When the Partner has no unused deposit, the **Lines** tab stays empty.
