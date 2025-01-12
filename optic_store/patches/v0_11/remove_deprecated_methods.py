import frappe

def execute():
    """Remove deprecated methods for ERPNext 15 compatibility"""
    try:
        # Remove old scheduler events
        deprecated_methods = [
            "optic_store.api.sales_invoice.write_off_expired_credit_notes",
            "optic_store.api.sms.process"  # SMS processing changed in v15
        ]
        
        for method in deprecated_methods:
            if method in frappe.get_hooks("daily"):
                frappe.db.delete(
                    "Scheduler Event",
                    {
                        "method": method
                    }
                )
        
        # Remove old doc events
        if "*" in frappe.get_hooks("doc_events"):
            events = frappe.get_hooks("doc_events").get("*", {})
            for event_type in ["after_insert", "on_update", "on_submit", "on_update_after_submit", "on_cancel"]:
                if "optic_store.api.sms.process" in events.get(event_type, []):
                    events[event_type].remove("optic_store.api.sms.process")
        
        frappe.db.commit()
    except Exception:
        pass  # Ignore if table or record doesn't exist 