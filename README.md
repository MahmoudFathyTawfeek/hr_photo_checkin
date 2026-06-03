### Hr Photo Checkin

Custom Frappe app that extends the Employee Checkin workflow in Frappe HR by introducing an optional photo requirement controlled through HR Settings.

## Features

* Added a custom checkbox field "Require Employee Checkin Photo" to *HR Settings* using Frappe Custom Fields and Fixtures.
* Added a custom **Attach Image** field (`custom_employee_photo`) to the **Employee Checkin** doctype for storing check-in photos.
* Registered a backend validation hook through `doc_events` in the custom app without modifying any HRMS source code.
* Implemented validation logic that checks the value of **Require Employee Checkin Photo** before saving an Employee Checkin record:

  * If the checkbox is enabled, a photo must be attached.
  * If the checkbox is disabled, the check-in can be saved without a photo.
* Exported all custom fields as fixtures to ensure they are version-controlled and can be deployed consistently across environments.

# Current Status

The backend validation workflow is complete and the photo requirement can be controlled directly from **HR Settings** through the custom toggle.
