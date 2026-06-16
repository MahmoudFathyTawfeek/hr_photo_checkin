import frappe


def get_context(context):
    """
    Controller for /photo-checkin page.
    - Requires login: redirect to login if not authenticated.
    - Passes employee info to context for the template.
    """

    # 1. Must be logged in
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/photo-checkin"
        raise frappe.Redirect

    # 2. Must have a linked Employee record
    employee = frappe.db.get_value(
        "Employee",
        {"user_id": frappe.session.user},
        ["name", "employee_name"],
        as_dict=True,
    )

    if not employee:
        frappe.throw(
            "No Employee record linked to your account. "
            "Please contact HR.",
            frappe.PermissionError,
        )

    # 3. Pass data to template (available as {{ employee_name }} etc.)
    context.employee_id = employee.name
    context.employee_name = employee.employee_name
    context.title = "Photo Check-in"
    context.no_cache = 1          # always fresh — no stale page on mobile