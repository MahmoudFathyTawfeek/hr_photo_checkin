### Hr Photo Checkin

Custom Frappe app that extends the Employee Checkin workflow in Frappe HR by introducing an optional photo requirement controlled through HR Settings.

### HR Settings Customization

A custom checkbox field named **Require Employee Checkin Photo** was added to the **HR Settings** doctype. The field was created as a Custom Field and exported through fixtures so that it becomes part of the application and can be deployed consistently across different environments.

This checkbox acts as a feature toggle that controls whether a photo is required during employee check-in.

### Employee Checkin Customization

A custom **Attach Image** field named **custom_employee_photo** was added to the **Employee Checkin** doctype. This field stores the photo captured or uploaded during the check-in process.

Like the HR Settings field, it is managed through fixtures and version controlled with the application.

### Validation Workflow

A validation hook was registered using `doc_events` in the application's `hooks.py` file.

Before a new Employee Checkin record is inserted:

1. The application reads the value of **Require Employee Checkin Photo** from HR Settings.
2. If the toggle is enabled, the system verifies that a photo exists in `custom_employee_photo`.
3. If no photo is attached, a validation error is raised and the check-in is rejected.
4. If the toggle is disabled, the validation is skipped and the check-in is saved normally.

This approach allows HR administrators to enable or disable photo enforcement without changing any code.

### List View Enhancement

The Employee Checkin List View was customized using `doctype_list_js`.

The custom script retrieves the `custom_employee_photo` field using `add_fields` and displays photo thumbnails directly within the Employee Checkin list. This provides a quick visual reference for check-in records without opening individual documents.

### Fixtures

All Custom Fields were exported as fixtures to ensure:

* Version control through Git.
* Consistent deployment across sites.
* No dependency on manual UI customization.
* Compliance with the Frappe custom app development pattern.

## Automated Tests

The application includes three automated tests implemented using `FrappeTestCase`.

To keep the tests focused on the validation logic, a lightweight `Doc` class is used to simulate an Employee Checkin document. The validation function only depends on the `custom_employee_photo` field, so there is no need to create actual Employee Checkin records during testing.

The value of the HR Settings toggle (`require_employee_checkin_photo`) is simulated by temporarily overriding `frappe.db.get_single_value`, allowing each scenario to be tested independently.

### Covered Scenarios

1. **Photo Required + Photo Provided**

   * The HR Settings toggle is enabled.
   * A photo is provided.
   * Validation succeeds without raising any errors.

2. **Photo Required + Photo Missing**

   * The HR Settings toggle is enabled.
   * No photo is provided.
   * Validation raises a `ValidationError`.

3. **Photo Not Required**

   * The HR Settings toggle is disabled.
   * No photo is provided.
   * Validation succeeds without raising any errors.

### Running Tests

bench --site localhost run-tests --app hr_photo_checkin

# Result
Ran 3 tests

OK

### Current Status

The backend implementation is complete and includes:

* HR Settings toggle for photo enforcement.
* Employee Checkin photo field.
* Backend validation logic.
* Employee Checkin List View photo thumbnails.
* Fixture-based customization management.

No modifications were made to HRMS or ERPNext source code.

========================================================================
## Week 2 — Frontend Architecture Decision

### The Problem
The task required extending the HRMS PWA to capture a photo 
during employee check-in. Two options were considered:

**Option 1: Fork HRMS**
- Clone HRMS and modify CheckInPanel.vue directly
- Modifies HRMS core code
- Creates merge conflicts on every HRMS update
- Long-term maintenance debt

**Option 2: Separate Route (Chosen)**
- Build a new page `/photo-checkin` inside the custom app
- Zero changes to HRMS source code
- All code lives inside our custom app
- Survives HRMS updates with no conflicts
- Tradeoff: Users access a different URL

# Why Override is Not Possible
HRMS PWA is a compiled Vue.js Single Page Application (SPA).
The components are compiled into a single minified JS bundle.
There is no way to override individual Vue components 
from an external app without modifying the source code directly.

# Frontend Implementation

# New Files

`www/photo-checkin.html` ---> Mobile camera UI 
`www/photo-checkin.py` -----> Server-side context provider 

# photo-checkin.py — What it does
- Redirects unauthenticated users to /login
- Fetches the employee ID linked to the logged-in user
- Fetches the employee name for display
- Provides CSRF token for secure API calls

# photo-checkin.html — What it does
- Opens rear camera automatically via getUserMedia()
- Shows live camera preview
- Captures photo on button click
- Shows preview with retake option
- On confirm: uploads photo and creates Employee Checkin record

## Full Check-in Flow

1. Employee opens `/photo-checkin` on mobile browser
2. Server verifies login → fetches employee data
3. Camera opens automatically (rear-facing)
4. Employee captures photo
5. Preview shown → can retake if needed
6. On confirm: Photo uploaded to Frappe file system
7. Record appears in Employee Checkin list view with thumbnail

## How to Run Locally

### Requirements
- Frappe bench running on port 8002
- ngrok for HTTPS (required for camera on mobile)

### Steps
1. Install app:
bash
   bench --site localhost install-app hr_photo_checkin
   bench --site localhost migrate


2. Start bench:
bash
   bench start


3. Start ngrok (in separate terminal):
bash
   ngrok http 8002 --host-header="localhost:8002"


4. Open on mobile: https://your-ngrok-url/photo-checkin
