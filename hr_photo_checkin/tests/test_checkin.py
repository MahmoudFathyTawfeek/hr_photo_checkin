from frappe.tests.utils import FrappeTestCase
import frappe

from hr_photo_checkin.hr_photo_checkin.checkin_validation import validate_checkin


class Doc:
    def __init__(self, photo):
        self.custom_employee_photo = photo


class TestCheckin(FrappeTestCase):

    def test_photo_required_with_photo(self):
        frappe.db.get_single_value = lambda *args: 1

        validate_checkin(Doc("/files/test.jpg"), None)

    def test_photo_required_without_photo(self):
        frappe.db.get_single_value = lambda *args: 1

        self.assertRaises(
            frappe.ValidationError,
            validate_checkin,
            Doc(None),
            None
        )

    def test_photo_not_required(self):
        frappe.db.get_single_value = lambda *args: 0

        validate_checkin(Doc(None), None)