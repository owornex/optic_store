# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute():
    if not frappe.db.exists("Custom Field", "Stock Entry-os_reference_stock_transfer"):
        frappe.get_doc(
            {
                "doctype": "Custom Field",
                "dt": "Stock Entry",
                "fieldname": "os_reference_stock_transfer",
                "fieldtype": "Data",
                "insert_after": "credit_note",
                "label": "Reference Stock Transfer",
                "translatable": 0,
                "read_only": 1,
            }
        ).insert()
    for doc in frappe.get_all(
        "Stock Transfer",
        fields=["name", "outgoing_stock_entry", "incoming_stock_entry"],
        filters=[["docstatus", "<", 2]],
    ):
        if doc.get("outgoing_stock_entry"):
            frappe.db.set_value(
                "Stock Entry",
                doc.get("outgoing_stock_entry"),
                "os_reference_stock_transfer",
                doc.get("name"),
            )
        if doc.get("incoming_stock_entry"):
            frappe.db.set_value(
                "Stock Entry",
                doc.get("incoming_stock_entry"),
                "os_reference_stock_transfer",
                doc.get("name"),
            )
