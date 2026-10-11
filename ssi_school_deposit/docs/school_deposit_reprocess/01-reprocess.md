# Reprocess School Deposit Realizations

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_reprocess`\
> **Menu:** School > School Deposit > Reprocess Deposit Realizations\
> **Actor:** user in group `Validator`

## Pre-Condition

- **Data:** A customer invoice is **Unpaid** and carries a line of a Payable Product,
  and was opened before the Partner's deposit was recorded.
- **Data:** The Partner now has an unused deposit of the deposit type.
- **Access:** User is in group `Validator`.

## Flow

1. Open the **School > School Deposit > Reprocess Deposit Realizations** menu.
2. In the dialog that appears, fill in the fields:
   - **Types** _(required)_: Select the deposit types to realize again.
   - **Partners**: Select the partners to limit the run to. Leave empty for all.
3. Click the **Reprocess** button.

## Post-Condition

- The dialog closes.
- Every **Unpaid** customer invoice that carries a Payable Product of the chosen types
  (and belongs to the chosen partners, if any) is settled with the available deposit,
  the same way as when it is opened. Each one gets a **Done** School Deposit
  Realization.
- Invoices without available deposit are left untouched.
