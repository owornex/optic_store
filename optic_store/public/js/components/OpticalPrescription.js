frappe.provide('optic_store.components');

optic_store.components.OpticalPrescription = class OpticalPrescription {
    constructor({ wrapper }) {
        this.wrapper = wrapper;
        this.make();
    }

    make() {
        this.init_component();
    }

    init_component() {
        this.prepare_dom();
        this.bind_events();
        this.load_data();
    }

    prepare_dom() {
        this.wrapper.innerHTML = `
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

        this.prescription_list = this.wrapper.querySelector('.prescription-list');
        this.no_prescriptions = this.wrapper.querySelector('.no-prescriptions');
    }

    bind_events() {
        this.wrapper.querySelector('.new-prescription').addEventListener('click', () => {
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
                    <h3>${prescription.customer_name}</h3>
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
} 