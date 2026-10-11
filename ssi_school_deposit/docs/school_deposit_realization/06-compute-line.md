# Compute Lines of School Deposit Realization

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_realization`\
> **Menu:** School > School Deposit > Deposit Realizations\
> **Actor:** user in group `User`\
> **State:** `draft`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** Status is **Draft**, with **Type**, **Partner** and **Customer Invoice**
  filled in.
- **Data:** The Customer Invoice is **Unpaid** and carries a line of a Payable Product
  of the Type.
- **Data:** The Partner has an unused deposit: a posted customer invoice line of a
  Deposit Product of the Type whose credit on the Deposit Account is not yet reconciled.
- **Access:** User is in group `User`.

## Flow

1. Open the **School > School Deposit > Deposit Realizations** menu.
2. Open the record to compute.
3. Click the **Compute Lines** button.

## Post-Condition

- The **Lines** tab lists one line per deposit journal item used, oldest first.
- The lines take from the deposit only up to the amount the invoice may still be settled
  with: the smaller of its unpaid amount and the value of its Payable Product lines,
  less any amount reserved for scheduled deductions.
- Lines entered earlier are replaced. **Amount Total** equals the sum of the lines.
- When the Partner has no unused deposit, the **Lines** tab stays empty.
