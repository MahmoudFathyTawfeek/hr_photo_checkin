frappe.listview_settings['Employee Checkin'] = {
    add_fields: ['custom_employee_photo'],

    before_render() {
        setTimeout(() => {

            cur_list.data.forEach(row => {

                if (!row.custom_employee_photo) return;

                document
                    .querySelectorAll(`a[data-name="${row.name}"]`)
                    .forEach(link => {

                        link.innerHTML =
                            `<img src="${row.custom_employee_photo}"
                                  style="width:30px;height:30px;border-radius:50%;margin-right:8px;">`
                            + link.innerHTML;
                    });
            });

        }, 300);
    }
};

