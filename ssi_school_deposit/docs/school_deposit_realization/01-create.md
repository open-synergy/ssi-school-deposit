# Create School Deposit Realization

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_realization`\
> **Menu:** School > School Deposit > Deposit Realizations\
> **Actor:** user in group `User`\
> **State:** `—` → `draft`

## Pre-Condition

- **Data:** A `school_deposit_type` exists (see `school_deposit_type/01-create`).
- **Data:** An open `customer_invoice` exists for the Partner whose deposit is used.
- **Data:** A posted deposit journal item exists for that Partner, credited to the
  Deposit Account of the Type and not yet fully reconciled.
- **Config:** The Realization Journal of the Type is not of type Bank or Cash.
- **Access:** User is in group `User`.

## Flow

1. Open the **School > School Deposit > Deposit Realizations** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Type** _(required)_: Select the deposit type. Selecting it defaults **Journal**
     from the Type's own Realization Journal.
   - **Partner** _(required)_: Select the partner who paid the deposit.
   - **Customer Invoice** _(required)_: Select an open invoice of that Partner.
   - **Date**: Defaults to today's date.
4. On the **Accounting** tab, check:
   - **Journal** _(required)_: Defaults from the Type; may be overridden. Bank and Cash
     journals are not offered.
5. On the **Lines** tab, add **at least one** line:
   - **Source Journal Item** _(required)_: Select a deposit credit journal item of the
     Partner on the Type's Deposit Account that still has an unreconciled credit.
     Selecting it defaults **Account**.
   - **Account** _(required)_: Defaults from the Type's Deposit Account.
   - **Amount** _(required)_: The portion of the deposit being used. Must be greater
     than zero.
6. Click **Save**.

## Post-Condition

- A new School Deposit Realization record is created in **Draft** status.
- **Amount Total** is the sum of the Lines' own Amount.
- Saving a line is rejected with an error if its Amount is zero or negative.
