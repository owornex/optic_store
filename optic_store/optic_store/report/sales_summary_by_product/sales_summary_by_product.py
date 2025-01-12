# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial, reduce
from toolz import (
    compose,
    pluck,
    merge,
    concatv,
    itemmap,
    unique,
    groupby,
    get,
    reduceby,
    valmap,
)

from optic_store.utils import pick, split_to_list, with_report_error_check, key_by
from optic_store.api.sales_invoice import get_payments_against
from optic_store.utils.report import make_column, with_report_generation_time


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    columns = concatv(
        [
            make_column(
                "invoice_name",
                "Sales Invoice",
                type="Link",
                options="Sales Invoice",
                width=150,
            ),
            make_column("invoice_date", type="Date", width=90),
            make_column("invoice_time", type="Time", width=90),
            make_column("brand", type="Link", options="Brand"),
            make_column("item_code", type="Link", options="Item"),
            make_column("item_group", type="Link", options="Item Group"),
            make_column("description"),
        ],
        [make_column("valuation_rate", "Cost Price", type="Currency", width=90)]
        if "Accounts Manager" in frappe.get_roles()
        else [],
        [
            make_column(
                "selling_rate", "Standard Selling Rate", type="Currency", width=90
            ),
            make_column("rate", "Sale Unit Rate", type="Currency", width=90),
            make_column("qty", type="Float", width=90),
        ],
        [make_column("valuation_amount", "Cost Amount", type="Currency", width=90)]
        if "Accounts Manager" in frappe.get_roles()
        else [],
        [
            make_column(
                "amount_before_discount",
                "Sale Amount Before Discount",
                type="Currency",
                width=90,
            ),
            make_column("discount_amount", type="Currency", width=90),
            make_column("discount_percentage", type="Percent", width=90),
            make_column(
                "amount_after_discount",
                "Sale Amount After Discount",
                type="Currency",
                width=90,
            ),
            make_column("ms1", "Minimum Selling Rate 1", type="Currency", width=90),
            make_column(
                "below_ms1",
                "Sold Below Mimimum Selling Rate 1",
                type="Select",
                options=["No", "Yes"],
                width=60,
            ),
            make_column("ms2", "Minimum Selling Rate 2", type="Currency", width=90),
            make_column(
                "below_ms2",
                "Sold Below Mimimum Selling Rate 2",
                type="Select",
                options=["No", "Yes"],
                width=60,
            ),
            make_column("total", "Invoice Total", type="Currency", width=90),
            make_column(
                "additional_discount_amount",
                "Invoice Additional Discount",
                type="Currency",
                width=90,
            ),
            make_column(
                "total_taxes_and_charges",
                "Invoice Taxes and Charges",
                type="Currency",
                width=90,
            ),
            make_column(
                "grand_total",
                "Invoice Grand Total",
                type="Currency",
                width=90,
            ),
            make_column("sales_person", type="Link", options="Employee"),
            make_column("sales_person_name", width="150"),
            make_column("commission_amount", type="Currency", width=90),
            make_column("remarks", type="Small Text", width=150),
            make_column("customer", type="Link", options="Customer"),
            make_column("customer_name", width="150"),
            make_column("notes", type="Small Text", width=150),
            make_column("dispensor", "Optometrist", type="Link", options="Employee"),
            make_column("branch", type="Link", options="Branch"),
            make_column(
                "sales_status", type="Select", options=["Achieved", "Collected"]
            ),
            make_column("collection_date", type="Date", width=90),
        ],
    )

    return list(columns)


def _get_filters(filters):
    branches = split_to_list(filters.branches)

    join_clauses = compose(" AND ".join, concatv)

    si_clauses = join_clauses(
        ["si.docstatus = 1"],
        ["si.os_branch IN %(branches)s"] if branches else [],
    )
    dn_clauses = join_clauses(
        [
            "dn.docstatus = 1",
            "dn.posting_date BETWEEN %(from_date)s AND %(to_date)s",
            "so.workflow_state = 'Collected'",
        ],
        ["dn.os_branch IN %(branches)s"] if branches else [],
    )

    values = merge(
        filters,
        {"branches": branches} if branches else {},
        {
            "selling_pl": "Standard Selling",
            "min_selling_pl1": "Minimum Selling",
            "min_selling_pl2": "Minimum Selling 2",
        },
    )
    return (
        {"si_clauses": si_clauses, "dn_clauses": dn_clauses},
        values,
    )


@with_report_error_check
def _get_data(clauses, values, keys):
    items, dates = _query(clauses, values)

    def add_collection_date(row):
        def get_collection_date(x):
            if x.sales_status == "Achieved":
                return None
            if x.own_delivery or x.is_return:
                # x.s_return because return delivery note is always considered to have
                # the same posting_date as that of the return sales invoice
                return x.invoice_date
            return dates.get(x.invoice_name)

        return merge(row, {"collection_date": get_collection_date(row)})

    def add_payment_remarks(items):
        payments = _get_payments(items)

        def fn(row):
            make_remark = compose(
                lambda x: ", ".join(x),
                partial(map, lambda x: "{mop}: {amount}".format(mop=x[0], amount=x[1])),
                lambda x: x.items(),
                lambda lines: reduceby(
                    "mode_of_payment",
                    lambda a, x: a + get("paid_amount", x, 0),
                    lines,
                    0,
                ),
                lambda x: concatv(
                    get(x.invoice_name, payments, []), get(x.order_name, payments, [])
                ),
                frappe._dict,
            )

            return merge(row, {"remarks": make_remark(row)})

        return fn

    def set_null(k, v):
        if v:
            return k, v
        if k not in [
            "valuation_rate",
            "selling_rate",
            "rate",
            "qty",
            "valuation_amount",
            "amount_before_discount",
            "discount_amount",
            "discount_percentage",
            "amount_after_discount",
            "ms1",
            "ms2",
            "commission_amount",
            "total",
            "additional_discount_amount",
            "total_taxes_and_charges",
            "grand_total",
        ]:
            return k, None
        return k, 0

    def remove_duplicates(columns):
        invoices = []

        def fn(row):
            invoice_name = row.get("invoice_name")
            if invoice_name not in invoices:
                invoices.append(invoice_name)
            else:
                return merge(row, {x: None for x in columns})
            return row

        return fn

    template = reduce(lambda a, x: merge(a, {x: None}), keys, {})
    make_row = compose(
        remove_duplicates(
            [
                "total",
                "additional_discount_amount",
                "total_taxes_and_charges",
                "grand_total",
            ]
        ),
        partial(pick, keys),
        partial(itemmap, lambda x: set_null(*x)),
        partial(merge, template),
        add_payment_remarks(items),
        add_collection_date,
    )

    return with_report_generation_time([make_row(x) for x in items], keys)


def _query(clauses, values):
    def get_delivered_invoices():
        if values.get("report_type") == "Achieved":
            return []
        get_invoices = compose(
            list,
            partial(unique, key=lambda x: x.get("invoice")),
            frappe.db.sql,
        )
        return get_invoices(
            """
                SELECT
                    IF(
                        dn.is_return = 1,
                        rsi.name,
                        dni.against_sales_invoice
                    ) AS invoice,
                    dn.posting_date AS delivery_date
                FROM `tabDelivery Note Item` AS dni
                LEFT JOIN `tabDelivery Note` AS dn ON
                    dn.name = dni.parent
                LEFT JOIN `tabSales Order` AS so ON
                    so.name = dni.against_sales_order
                LEFT JOIN `tabSales Invoice` AS rsi ON
                    rsi.is_return = dn.is_return AND
                    rsi.return_against = dni.against_sales_invoice
                WHERE {dn_clauses}
            """.format(
                **clauses
            ),
            values=values,
            as_dict=1,
        )

    invoices = get_delivered_invoices()

    def get_other_clauses():
        if values.get("report_type") == "Achieved":
            return "si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
        collected_clause = """
            si.update_stock = 1 AND
            si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        """
        if not invoices:
            return collected_clause
        return "({} OR si.name IN %(invoices)s)".format(collected_clause)

    items = frappe.db.sql(
        """
            SELECT
                si.name AS invoice_name,
                sii.sales_order AS order_name,
                si.posting_date AS invoice_date,
                si.posting_time AS invoice_time,
                sii.brand AS brand,
                sii.item_code AS item_code,
                sii.item_group AS item_group,
                sii.description AS description,
                bp.valuation_rate AS valuation_rate,
                sii.price_list_rate AS selling_rate,
                sii.rate AS rate,
                sii.qty AS qty,
                sii.qty * IFNULL(bp.valuation_rate, 0) AS valuation_amount,
                IF(
                    sii.discount_percentage = 100,
                    sii.price_list_rate * sii.qty,
                    sii.amount * 100 / (100 - sii.discount_percentage)
                ) AS amount_before_discount,
                IF(
                    sii.discount_percentage = 100,
                    sii.price_list_rate * sii.qty,
                    sii.amount * (100 / (100 - sii.discount_percentage) - 1)
                ) AS discount_amount,
                sii.discount_percentage AS discount_percentage,
                sii.amount AS amount_after_discount,
                sii.os_minimum_selling_rate AS ms1,
                IF(
                    (sii.amount / sii.qty) < sii.os_minimum_selling_rate,
                    'Yes',
                    'No'
                ) AS below_ms1,
                sii.os_minimum_selling_2_rate AS ms2,
                IF(
                    (sii.amount / sii.qty) < sii.os_minimum_selling_2_rate,
                    'Yes',
                    'No'
                ) AS below_ms2,
                si.os_sales_person AS sales_person,
                si.os_sales_person_name AS sales_person_name,
                IF(
                    si.total = 0,
                    0,
                    si.total_commission * sii.amount / si.total
                ) AS commission_amount,
                si.customer AS customer,
                si.customer_name AS customer_name,
                si.os_notes AS notes,
                si.orx_dispensor AS dispensor,
                si.os_branch AS branch,
                IF(
                    si.update_stock = 1 OR so.workflow_state = 'Collected',
                    'Collected',
                    'Achieved'
                ) AS sales_status,
                si.update_stock AS own_delivery,
                si.is_return AS is_return,
                si.discount_amount AS additional_discount_amount,
                si.total_taxes_and_charges,
                si.total,
                si.grand_total
            FROM `tabSales Invoice Item` AS sii
            LEFT JOIN `tabSales Invoice` AS si ON
                si.name = sii.parent
            LEFT JOIN `tabSales Order` AS so ON
                so.name = sii.sales_order
            LEFT JOIN `tabBin` AS bp ON
                bp.item_code = sii.item_code AND
                bp.warehouse = sii.warehouse
            WHERE {si_clauses} AND {other_clauses}
            ORDER BY invoice_date
        """.format(
            other_clauses=get_other_clauses(), **clauses
        ),
        values=merge(
            values,
            {"invoices": [x.get("invoice") for x in invoices]},
        ),
        as_dict=1,
    )

    def get_dates():
        make_dates = compose(
            partial(valmap, lambda x: x.get("delivery_date")),
            partial(key_by, "invoice"),
        )

        if values.get("report_type") == "Collected":
            return make_dates(invoices)
        if not items:
            return {}

        filter_invoices = compose(
            partial(unique, key=lambda x: x.get("invoice_name")),
            partial(filter, lambda x: not x.get("own_delivery")),
        )
        dates = frappe.db.sql(
            """
                SELECT
                    dni.against_sales_invoice AS invoice,
                    dn.posting_date AS delivery_date
                FROM `tabDelivery Note Item` AS dni
                LEFT JOIN `tabDelivery Note` AS dn ON
                    dn.name = dni.parent
                LEFT JOIN `tabSales Invoice` AS si ON
                    si.name = dni.against_sales_invoice
                WHERE dni.against_sales_invoice IN %(invoices)s
            """,
            values={
                "invoices": [x.get("invoice_name") for x in filter_invoices(items)]
            },
            as_dict=1,
        )

        return make_dates(dates)

    return items, get_dates()


def _get_payments(items):
    def get_names(key):
        return compose(list, unique, partial(pluck, key))(items)

    invoices = get_names("invoice_name")

    si_payments = frappe.db.sql(
        """
            SELECT parent AS reference_name, mode_of_payment, amount AS paid_amount
            FROM `tabSales Invoice Payment` WHERE parent IN %(invoices)s
        """,
        values={"invoices": invoices},
        as_dict=1,
    )
    payments_against_si = get_payments_against("Sales Invoice", invoices)
    payments_against_so = get_payments_against("Sales Order", get_names("order_name"))

    return groupby(
        "reference_name", concatv(si_payments, payments_against_si, payments_against_so)
    )
