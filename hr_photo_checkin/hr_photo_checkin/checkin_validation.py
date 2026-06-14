

import frappe
from frappe.utils.file_manager import save_file

def validate_checkin(doc, method):
    required = frappe.db.get_single_value(
        "HR Settings",
        "require_employee_checkin_photo"
    )

    if required:
        if not doc.custom_employee_photo:
            frappe.throw("Employee photo is required for check-in")

    if doc.custom_employee_photo:
        frappe.db.set_value("File", {"file_url":doc.custom_employee_photo}, "is_private", 0)
        frappe.db.commit()


