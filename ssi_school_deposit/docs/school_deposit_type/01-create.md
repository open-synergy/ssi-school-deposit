# Create School Deposit Type

> **Module:** `ssi_school_deposit`\
> **Model:** `school_deposit_type`\
> **Menu:** School > Configuration > School Deposit > School Deposit Types\
> **Actor:** user in group `School Deposit Type`

## Pre-Condition

- **Data:** An account that allows reconciliation exists, to hold the deposit liability.
- **Data:** A journal that is not of type Bank or Cash exists, for the realization
  entries.
- **Data:** The products that identify a deposit invoice line, and the products a
  deposit may settle, exist.
- **Access:** User is in group `School Deposit Type`.

## Flow

1. Open the **School > Configuration > School Deposit > School Deposit Types** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Name** _(required)_: Enter the name of the deposit type (e.g. "Re-enrollment
     Deposit").
   - **Code** _(required)_: Enter a unique code identifying this deposit type, or enter
     **/** to assign it later using **Generate Code**.
   - **Deposit Account** _(required)_: Select the liability account credited when a
     deposit invoice is posted. Only an account that allows reconciliation is accepted.
   - **Realization Journal** _(required)_: Select the journal in which realizations of
     this type are posted. Bank and Cash journals are not offered.
   - **Forfeit Journal**: Optionally select the journal in which forfeits of this type
     are posted. Bank and Cash journals are not offered. Required before a School
     Deposit Forfeit of this type can be finished.
   - **Forfeit Account**: Optionally select the account credited when an unused deposit
     of this type is forfeited. Required before a School Deposit Forfeit of this type
     can be finished.
   - **Auto Realize**: Checked by default. Uncheck it to create realizations of this
     type by hand only.
4. On the **Products** tab, fill in:
   - **Deposit Products** _(required)_: Select the products whose invoice lines record a
     deposit of this type.
   - **Payable Products** _(required)_: Select the products this deposit may be used to
     settle.
5. Click **Save**.

## Post-Condition

- A new School Deposit Type record is created and active.
- The type becomes selectable on a School Deposit Realization.
- Saving is rejected with an error if the Deposit Account does not allow reconciliation.
