# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("Documents"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Optical Prescription",
                    "description": _("Manage optical prescriptions"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Sales Order",
                    "description": _("Manage sales orders"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Sales Invoice",
                    "description": _("Manage sales invoices"),
                    "onboard": 1,
                }
            ]
        },
        {
            "label": _("Setup"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Branch",
                    "description": _("Manage branches"),
                },
                {
                    "type": "doctype",
                    "name": "Sales Person",
                    "description": _("Manage sales persons"),
                }
            ]
        }
    ]
