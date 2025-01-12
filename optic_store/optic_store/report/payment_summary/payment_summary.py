# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from functools import partial
from toolz import compose, pluck, merge, concatv

from optic_store.utils import pick, split_to_list
from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    columns = _get_columns()
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns():
    return [
        make_column("posting_date", "Payment Date", type="Date", width=90),
        make_column("posting_time", "Payment Time", type="Time", width=90),
        make_column("voucher_type"),
        make_column("voucher_no", type="Dynamic Link", options="voucher_type"),
        make_column("mode_of_payment", type="Link", options="Mode of Payment"),
        make_column("paid_amount", "Payment Amount", type="Currency"),
        make_column("customer", type="Link", options="Customer"),
        make_column("customer_name", width=150),
        make_column("branch", type="Link", options="Branch"),
        make_column("sales_person", type="Link", options="Employee"),
        make_column("sales_person_name", width=150),
    ]


def _get_filters(filters):
    modes_of_payment = split_to_list(filters.modes_of_payment)
    branches = split_to_list(filters.branches)
    si_clauses = concatv(
        ["si.docstatus = 1", "si.posting_date BETWEEN %(start_date)s AND %(end_date)s"],
        ["si.is_return = 0"] if cint(filters.hide_returns) else [],
        ["si.os_branch IN %(branches)s"] if branches else [],
        ["sip.mode_of_payment IN %(modes_of_payment)s"] if modes_of_payment else [],
    )
    pe_clauses = concatv(
        [
            "pe.docstatus = 1",
            "pe.party_type = 'Customer'",
            "pe.posting_date BETWEEN %(start_date)s AND %(end_date)s",
        ],
        ["pe.payment_type = 'Receive'"] if cint(filters.hide_returns) else [],
        ["pe.os_branch IN %(branches)s"] if branches else [],
        ["pe.mode_of_payment IN %(modes_of_payment)s"] if modes_of_payment else [],
    )
    values = merge(
        pick(["start_date", "end_date"], filters),
        {"branches": branches} if branches else {},
        {"modes_of_payment": modes_of_payment} if modes_of_payment else {},
    )
    return (
        {
            "si_clauses": " AND ".join(si_clauses),
            "pe_clauses": " AND ".join(pe_clauses),
        },
        values,
    )


def _get_data(clauses, values, keys):
    # UNION ALL for minor performance gain
    result = frappe.db.sql(
        """
            SELECT
                si.posting_date AS posting_date,
                si.posting_time AS posting_time,
                'Sales Invoice' AS voucher_type,
                si.name AS voucher_no,
                sip.mode_of_payment AS mode_of_payment,
                sip.amount AS paid_amount,
                si.customer AS customer,
                si.customer_name AS customer_name,
                si.os_sales_person AS sales_person,
                si.os_sales_person_name AS sales_person_name,
                si.os_branch AS branch
            FROM `tabSales Invoice` AS si
            RIGHT JOIN `tabSales Invoice Payment` AS sip ON sip.parent = si.name
            WHERE {si_clauses}
            UNION ALL
            SELECT
                pe.posting_date AS posting_date,
                pe.os_posting_time AS posting_time,
                'Payment Entry' AS voucher_type,
                pe.name AS voucher_no,
                pe.mode_of_payment AS mode_of_payment,
                pe.paid_amount AS paid_amount,
                pe.party AS customer,
                pe.party_name AS customer_name,
                per.sales_person AS sales_person,
                per.sales_person_name AS sales_person_name,
                pe.os_branch AS branch
            FROM `tabPayment Entry` AS pe
            RIGHT JOIN (
                SELECT
                    rjper.parent AS parent,
                    rjsi.os_sales_person AS sales_person,
                    rjsi.os_sales_person_name AS sales_person_name
                FROM `tabPayment Entry Reference` AS rjper
                LEFT JOIN `tabSales Invoice` AS rjsi ON rjsi.name = rjper.reference_name
                WHERE rjper.reference_doctype = 'Sales Invoice'
            ) AS per ON per.parent = pe.name
            WHERE {pe_clauses}
            ORDER BY posting_date, posting_time
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )

    make_row = partial(pick, keys)
    return with_report_generation_time([make_row(x) for x in result], keys)
