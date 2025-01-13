frappe.pages['optical-prescription'].on_page_load = function(wrapper) {
    frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Optical Prescriptions'),
        single_column: true
    });

    frappe.require([
        '/assets/optic_store/css/optical_prescription.css',
        '/assets/optic_store/js/components/OpticalPrescription.js'
    ], () => {
        wrapper.optical_prescription = new optic_store.components.OpticalPrescription({
            wrapper: wrapper.page.main
        });
    });
}; 