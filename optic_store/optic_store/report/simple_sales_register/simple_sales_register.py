# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck, keyfilter, concatv

from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    columns = _get_columns()
    keys = _get_keys()
    data = _get_data(_get_clauses(filters), filters, keys)
    return columns, data


def _get_columns():
    return [
        make_column("posting_date", "Date", type="Date", width=90),
        make_column("invoice", "Invoice No", type="Link", options="Sales Invoice"),
        make_column("customer", type="Link", options="Customer"),
        make_column("total", type="Currency"),
        make_column("discount", type="Currency"),
        make_column("net_total", type="Currency"),
        make_column("tax", type="Currency"),
        make_column("grand_total", type="Currency"),
    ]


def _get_keys():
    return compose(list, partial(pluck, "fieldname"), _get_columns)()


def _get_clauses(filters):
    if not filters.get("company"):
        frappe.throw(_("Company is required to generate report"))
    invoice_type = {"Sales": 0, "Returns": 1}
    clauses = concatv(
        [
            "docstatus = 1",
            "company = %(company)s",
            "posting_date BETWEEN %(from_date)s AND %(to_date)s",
        ],
        ["customer = %(customer)s"] if filters.get("customer") else [],
        ["is_return = {}".format(invoice_type[filters.get("invoice_type")])]
        if filters.get("invoice_type") in invoice_type
        else [],
    )
    return " AND ".join(clauses)


def _get_data(clauses, args, keys):
    items = frappe.db.sql(
        """
            SELECT
                posting_date,
                name AS invoice,
                customer,
                base_total AS total,
                base_discount_amount AS discount,
                base_net_total AS net_total,
                base_total_taxes_and_charges AS tax,
                base_grand_total AS grand_total
            FROM `tabSales Invoice`
            WHERE {clauses}
        """.format(
            clauses=clauses
        ),
        values=args,
        as_dict=1,
    )

    make_row = partial(keyfilter, lambda k: k in keys)
    return with_report_generation_time([make_row(x) for x in items], keys)
