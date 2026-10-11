# Create School Deposit Realization

> **Module:** `ssi_school_deposit_operating_unit`\
> **Extends:** ssi_school_deposit — model `school_deposit_realization`, aksi `01-create`

## Additional Pre-Condition

- **Module:** The `operating_unit` module is installed.
- **Data:** At least one active `operating.unit` record exists.
- **Access:** Only a user in group `operating_unit.group_multi_operating_unit` sees and
  can edit the Operating Unit field described below; a user outside that group creates
  the realization exactly as documented in the base IK, with the field hidden.

## Additional Fields

When this module is installed, the create form gains one field:

- **Operating Unit**: The operating unit this realization belongs to. Defaults to the
  creating user's default operating unit (`default_operating_unit_id`) and follows the
  Operating Unit of the selected **Customer Invoice** as soon as one is chosen. It may
  be changed while still in Draft, but the realization cannot be confirmed or finished
  while it differs from the Operating Unit of its Customer Invoice. Becomes read-only
  once the realization leaves Draft.

## Modified — Record Visibility

- The Deposit Realization list is now filtered by operating unit (record rule). A user
  in group `Operating Unit` only sees realizations whose Operating Unit is among the
  operating units assigned to them. This is not a Flow step.

## Additional Post-Condition

- When the realization later reaches **Done** (see base IK `ssi_school_deposit`
  `docs/school_deposit_realization/07-approve.md`), the `account.move` created for it
  carries the same Operating Unit as the realization, regardless of the default
  operating unit of the user who approves it.
- When a line takes its deposit from a journal item recorded in **another** operating
  unit, finishing the realization books two journals instead of one: the main journal in
  the realization's own operating unit (receivable credited, **Interunit Account** of
  the Type debited) and an additional journal in the operating unit of the deposit
  (deposit account debited, Interunit Account credited). Both Interunit Account lines
  are reconciled, so the account ends with a zero balance, and the additional journal is
  listed under **Interunit Journal Entries** on the **Accounting** tab.
- Cancelling a done interunit realization deletes both journals.
