frappe.ui.form.on('Employee Checkin', {
    refresh(frm) {
        if (window.innerWidth <= 768 ) {
            setTimeout(() => {
                const field = frm.get_field("custom_employee_photo");
                if (field && field.$wrapper) {
                    field.$wrapper.find("button").off("click.camera").on("click.camera", function(e) {
                        e.preventDefault();
                        e.stopImmediatePropagation();
                        openCameraModal(frm);
                    });
                }
            }, 500);
        }

        // استقبل الصورة من الـ iframe
        window.addEventListener("message", function(event) {
            if (event.data && event.data.type === "photo_captured") {
                frm.set_value("custom_employee_photo", event.data.photoUrl);
                closeCameraModal();
            }
        });
    }
});

function openCameraModal(frm) {
    // اعمل overlay بـ iframe
    const overlay = document.createElement("div");
    overlay.id = "camera-overlay";
    overlay.style.cssText = `
        position: fixed; inset: 0; z-index: 9999;
        background: #fff;
    `;
    overlay.innerHTML = `
        <iframe 
            src="/photo-checkin?mode=embed" 
            style="width:100%; height:100%; border:none;">
        </iframe>
    `;
    document.body.appendChild(overlay);
}

function closeCameraModal() {
    const overlay = document.getElementById("camera-overlay");
    if (overlay) overlay.remove();
}