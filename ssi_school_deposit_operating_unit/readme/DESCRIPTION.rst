Glue module between School Deposit and Operating Unit. It is installed
automatically when both are installed.

* A deposit realization and a deposit forfeit belong to a single operating
  unit, are restricted by a record rule, and are booked in that unit.
* A realization takes the operating unit of the customer invoice it settles.
* A realization may use a deposit recorded in another operating unit. It is
  then booked as two journals: the main journal in the realization's unit and
  an additional journal in the unit of the deposit, joined by the *Interunit
  Account* configured on the deposit type. The two lines on that account are
  reconciled, so the deposit balance of the source unit decreases while the
  receivable of the target unit is settled.
* A deposit can only be forfeited in the operating unit that recorded it.
