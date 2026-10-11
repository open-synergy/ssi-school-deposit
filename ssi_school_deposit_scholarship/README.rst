.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
School Deposit - Scholarship
============================

Glue module between School Deposit and School Scholarship. It is
installed automatically when both are installed.

* A deposit realization no longer uses the room of a scholarship
  deduction that is already scheduled on the invoice. It reserves the
  planned amount of every scheduled schedule line of an open or done
  scholarship award billed by the invoice and settles only the rest,
  so the scholarship deduction can still be finished afterwards. A
  schedule line that is already realized is not reserved again.


Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/ssi-school-deposit
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list (Must be on developer mode)
4.  Go to menu *Apps -> Apps -> Main Apps*
5.  Search For *School Deposit - Scholarship*
6.  Install the module


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/open-synergy/ssi-school-deposit/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Andhitia Rama <andhitia.r@gmail.com>

Maintainer
----------

.. image:: https://simetri-sinergi.id/logo.png
   :alt: PT. Simetri Sinergi Indonesia
   :target: https://simetri-sinergi.id

This module is maintained by the PT. Simetri Sinergi Indonesia.
