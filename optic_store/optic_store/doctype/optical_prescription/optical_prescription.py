# -*- coding: utf-8 -*-
# Copyright (c) 2024, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class OpticalPrescription(Document):
    def validate(self):
        self.set_status()
        self.validate_dates()

    def on_submit(self):
        self.status = 'Active'

    def on_cancel(self):
        self.status = 'Cancelled'

    def set_status(self):
        if self.docstatus == 0:
            self.status = 'Draft'
        elif self.docstatus == 1:
            if not self.status:
                self.status = 'Active'
        elif self.docstatus == 2:
            self.status = 'Cancelled'

    def validate_dates(self):
        if self.test_date and frappe.utils.getdate(self.test_date) > frappe.utils.getdate():
            frappe.throw('Test Date cannot be in the future')
