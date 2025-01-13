# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "module_name": "Optic Store",
            "color": "grey",
            "icon": "octicon octicon-file-directory",
            "type": "module",
            "label": _("Optic Store"),
        },
        {
            "module_name": "Optical Prescription",
            "color": "blue",
            "icon": "fa fa-file-text-o",
            "type": "page",
            "link": "optical-prescription",
            "label": _("Optical Prescription")
        }
    ]
