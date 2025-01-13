# -*- coding: utf-8 -*-
from . import __version__ as app_version

app_name = "optic_store"
app_title = "Optic Store"
app_publisher = "9T9IT"
app_description = "ERPNext App for Optical Store"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@9t9it.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = ["/assets/css/optic_store.min.css"]
app_include_js = ["/assets/js/optic_store.min.js"]

# include js, css files in header of web template
# web_include_css = "/assets/optic_store/css/optic_store.css"
# web_include_js = "/assets/optic_store/js/optic_store.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "optic_store/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
page_js = {
    "optical-prescription": "public/js/pages/optical_prescription.js"
}

# include js in doctype views
doctype_js = {
    "Sales Order": "public/js/transaction_controller.js",
    "Sales Invoice": "public/js/transaction_controller.js",
    "Delivery Note": "public/js/transaction_controller.js",
}

doctype_list_js = {
    "Sales Invoice": "public/js/sales_invoice_list.js",
    "Stock Entry": "public/js/stock_entry_list.js",
}

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Optical Prescription": "optic_store.optic_store.doctype.optical_prescription.optical_prescription.OpticalPrescription"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Order": {
        "before_naming": "optic_store.doc_events.sales_order.before_naming",
        "validate": "optic_store.doc_events.sales_order.validate",
        "before_insert": "optic_store.doc_events.sales_order.before_insert",
        "before_save": "optic_store.doc_events.sales_order.before_save",
        "before_submit": "optic_store.doc_events.sales_order.before_submit",
        "on_update": "optic_store.doc_events.sales_order.on_update",
        "before_cancel": "optic_store.doc_events.sales_order.before_cancel",
    },
    "Sales Invoice": {
        "before_naming": "optic_store.doc_events.sales_invoice.before_naming",
        "validate": "optic_store.doc_events.sales_invoice.validate",
        "before_insert": "optic_store.doc_events.sales_invoice.before_insert",
        "before_save": "optic_store.doc_events.sales_invoice.before_save",
        "before_submit": "optic_store.doc_events.sales_invoice.before_submit",
        "on_submit": "optic_store.doc_events.sales_invoice.on_submit",
        "on_update_after_submit": "optic_store.doc_events.sales_invoice.on_update_after_submit",
        "before_cancel": "optic_store.doc_events.sales_invoice.before_cancel",
        "on_cancel": "optic_store.doc_events.sales_invoice.on_cancel",
    }
}

# Fixtures
# ---------------
fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "Sales Order-os_order_type",
                    "Sales Order-os_branch",
                    "Sales Order-os_item_type",
                    "Sales Order-os_sales_person",
                    "Sales Order-os_sales_person_name",
                    "Sales Invoice-os_branch",
                    "Sales Invoice-os_sales_person",
                    "Sales Invoice-os_sales_person_name"
                ]
            ]
        ]
    }
]

# Translation
# ------------------
translation_dirs = ['translations']
lang_map = {
    'pt-BR': ['pt', 'pt-br'],
}
