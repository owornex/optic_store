import frappe

def execute():
    """Update POS methods for ERPNext 15 compatibility"""
    try:
        # Add new required methods
        new_methods = {
            "erpnext.selling.page.point_of_sale.point_of_sale.get_loyalty_programs": "optic_store.api.pos.get_loyalty_programs",
            "erpnext.selling.page.point_of_sale.point_of_sale.get_invoice_summary": "optic_store.api.pos.get_invoice_summary"
        }
        
        for method_path, override_path in new_methods.items():
            if not frappe.db.exists("DocType Override", {
                "parent": "optic_store",
                "override_doctype": "point_of_sale.point_of_sale",
                "method": method_path
            }):
                frappe.get_doc({
                    "doctype": "DocType Override",
                    "parent": "optic_store",
                    "override_doctype": "point_of_sale.point_of_sale",
                    "method": method_path,
                    "override_method": override_path
                }).insert()
        
        frappe.db.commit()
    except Exception:
        pass  # Ignore if table or record doesn't exist 