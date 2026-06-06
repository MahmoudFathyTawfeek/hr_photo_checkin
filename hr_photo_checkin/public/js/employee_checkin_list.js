

frappe.listview_settings['Employee Checkin'] = {
    add_fields: ['custom_employee_photo'],
    formatters: {
        custom_employee_photo(value) {
            if (value) {
               
                return `<img src="${value}" style="width:50px;height:50px;border-radius:20%;">`;

            }
            return "";
        }
    }
}