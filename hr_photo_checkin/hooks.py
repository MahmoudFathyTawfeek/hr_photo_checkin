app_name = "hr_photo_checkin"
app_title = "Hr Photo Checkin"
app_publisher = "Mahmoud Tawfeek"
app_description = "this app to add photo to employee checkin"
app_email = "mahmoudtawfeek815@gmail.com"
app_license = "mit"

fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "HR Settings-require_employee_checkin_photo",
                    "Employee Checkin-custom_employee_photo"
                ]
            ]
        ]
    }
]

doc_events = {
    "Employee Checkin": {
        "before_insert": "hr_photo_checkin.hr_photo_checkin.checkin_validation.validate_checkin"
    }
}

doctype_list_js = {
    "Employee Checkin": "public/js/employee_checkin_list.js"
}

doctype_js = {
    "Employee Checkin": "public/js/employee_checkin.js"
}