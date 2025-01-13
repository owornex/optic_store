from frappe import _

def get_data():
    return [
        {
            "label": _("Optical Store"),
            "icon": "octicon octicon-file-directory",
            "items": [
                {
                    "type": "page",
                    "name": "optical-prescription",
                    "label": _("Optical Prescription"),
                    "description": _("Manage optical prescriptions"),
                    "icon": "fa fa-file-text-o",
                }
            ]
        }
    ] 