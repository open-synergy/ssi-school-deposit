# Automatic School Deposit Realization on Opening an Invoice

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_realization`\
> **Menu:** Financial Accounting > Account Receivable > Customer Invoice\
> **Actor:** system, triggered by approving a customer invoice\
> **State:** `draft` → `done`\
> **Requires:** `01-create`

## Pre-Condition

- **Record:** A customer invoice is **Waiting for Approval**, and has a line of a
  Payable Product of a deposit type with **Auto Realize** checked.
- **Data:** The invoice Partner has an unused deposit of that type (see
  `06-compute-line`).
- **Access:** User can approve the customer invoice.

## Flow

1. Open the **Financial Accounting > Account Receivable > Customer Invoice** menu.
2. Open the invoice to approve.
3. Click the **Approve** button.
4. Click **OK** on the confirmation dialog.

## Post-Condition

- The invoice becomes **Unpaid**, and then **Paid** when the deposit covers it fully. A
  deposit smaller than the invoice leaves the invoice **Unpaid** with the rest due.
- A School Deposit Realization of the Partner and the invoice is listed under **School >
  School Deposit > Deposit Realizations** with status **Done**. It settles the smaller
  of the unpaid amount and the value of the Payable Product lines, taking from the
  oldest deposit first. The rest of the deposit stays for later invoices.
- When no deposit is available no realization is created.
- When finishing the realization fails, it stays **Draft** and a note is posted on the
  invoice; the invoice itself is still **Unpaid**.
