# Create School Deposit Forfeit

> **Module:** `ssi_school_deposit_operating_unit`\
> **Extends:** ssi_school_deposit — model `school_deposit_forfeit`, aksi `01-create`

## Additional Pre-Condition

- **Module:** The `operating_unit` module is installed.
- **Data:** At least one active `operating.unit` record exists.
- **Access:** Only a user in group `operating_unit.group_multi_operating_unit` sees and
  can edit the Operating Unit field described below; a user outside that group creates
  the forfeit exactly as documented in the base IK, with the field hidden.

## Additional Fields

When this module is installed, the create form gains one field:

- **Operating Unit**: The operating unit this forfeit belongs to. Defaults to the
  creating user's default operating unit (`default_operating_unit_id`); may be changed
  while still in Draft. Becomes read-only once the forfeit leaves Draft. A deposit is
  always forfeited in the operating unit that recorded it.

## Modified — Record Visibility

- The Deposit Forfeit list is now filtered by operating unit (record rule). A user in
  group `Operating Unit` only sees forfeits whose Operating Unit is among the operating
  units assigned to them. This is not a Flow step.

## Modified Validation

- Finish is rejected with an error **if** a line takes its deposit from a journal item
  recorded in another operating unit than the forfeit's own.

## Additional Post-Condition

- When the forfeit later reaches **Done** (see base IK `ssi_school_deposit`
  `docs/school_deposit_forfeit/04-approve.md`), the `account.move` created for it
  carries the same Operating Unit as the forfeit.
