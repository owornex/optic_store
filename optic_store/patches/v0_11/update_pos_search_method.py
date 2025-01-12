import frappe

def execute():
    """Update POS search method for ERPNext 15 compatibility"""
    try:
        # Remove the old method override
        frappe.db.delete(
            "DocType Override",
            {
                "parent": "optic_store",
                "override_doctype": "point_of_sale.point_of_sale",
                "method": "search_serial_or_batch_or_barcode_number"
            }
        )
        frappe.db.commit()
    except Exception:
        pass  # Ignore if table or record doesn't exist 