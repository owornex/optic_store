frappe.provide('optic_store.pages.optical_prescription');

frappe.pages['optical-prescription'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Optical Prescriptions'),
        single_column: true
    });

    // Add page to window for access
    frappe.optical_prescription = page;
    
    // Initialize page
    new optic_store.pages.optical_prescription.OpticalPrescriptionPage(page);
};

optic_store.pages.optical_prescription.OpticalPrescriptionPage = class OpticalPrescriptionPage {
    constructor(page) {
        this.page = page;
        this.make();
    }

    make() {
        this.page.main.innerHTML = `
            <div class="optical-prescription">
                <div class="prescription-header">
                    <h2>${__('Optical Prescription')}</h2>
                    <button class="btn btn-primary new-prescription">
                        ${__('New Prescription')}
                    </button>
                </div>
                <div class="prescription-list"></div>
                <div class="no-prescriptions text-muted text-center hide">
                    ${__('No prescriptions found')}
                </div>
            </div>
        `;

        this.prescription_list = this.page.main.querySelector('.prescription-list');
        this.no_prescriptions = this.page.main.querySelector('.no-prescriptions');
        
        this.bind_events();
        this.load_data();
    }

    bind_events() {
        this.page.main.querySelector('.new-prescription').addEventListener('click', () => {
            frappe.new_doc('Optical Prescription');
        });
    }

    load_data() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Optical Prescription',
                fields: ['name', 'customer', 'customer_name', 'test_date', 'type'],
                filters: { docstatus: 1 },
                order_by: 'test_date desc'
            },
            callback: (response) => {
                if (response.message && response.message.length) {
                    this.render_prescriptions(response.message);
                } else {
                    this.show_no_prescriptions();
                }
            }
        });
    }

    render_prescriptions(prescriptions) {
        this.prescription_list.innerHTML = prescriptions.map(prescription => `
            <div class="prescription-card" data-name="${prescription.name}">
                <div class="prescription-info">
                    <h3>${prescription.customer_name || prescription.customer}</h3>
                    <div class="prescription-details">
                        <span>${prescription.type || 'Standard'}</span>
                        <span>${frappe.datetime.str_to_user(prescription.test_date)}</span>
                    </div>
                </div>
                <button class="btn btn-default btn-xs view-prescription">
                    ${__('View')}
                </button>
            </div>
        `).join('');

        this.prescription_list.querySelectorAll('.view-prescription').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const name = e.target.closest('.prescription-card').dataset.name;
                frappe.set_route('Form', 'Optical Prescription', name);
            });
        });

        this.no_prescriptions.classList.add('hide');
        this.prescription_list.classList.remove('hide');
    }

    show_no_prescriptions() {
        this.prescription_list.classList.add('hide');
        this.no_prescriptions.classList.remove('hide');
    }
}; 