import Vue from 'vue/dist/vue.js';

import PrescriptionForm from '../components/PrescriptionForm.vue';
import {
  get_all_rx_params,
  get_signed_fields,
  get_prec2_fields,
} from '../utils/constants';
import { format } from '../utils/format';

function handle_reading(side) {
  const params = ['sph', 'cyl', 'axis', 'va', 'bc', 'dia'];
  return async function(frm) {
    return Promise.all(
      params.map(param => {
        const dval = frm.doc[`${param}_${side}`];
        const field = `${param}_reading_${side}`;
        if (dval) {
          const rval =
            param === 'sph'
              ? format(
                  field,
                  parseFloat(dval || 0) + parseFloat(frm.doc[`add_${side}`] || 0)
                )
              : dval;
          return frm.set_value(field, rval);
        }
      })
    );
  };
}

function toggle_detail_entry(frm, state) {
  frm.toggle_display('details_simple_sec', !state);
  frm.toggle_display(['details_sec', 'pd_sec', 'prism_sec', 'iop_sec'], state);
}

function calc_total_pd(frm) {
  const { pd_right = 0, pd_left = 0 } = frm.doc;
  const fval = parseFloat(pd_right) + parseFloat(pd_left);
  return frm.set_value('pd_total', fval.toFixed(1));
}

function update_fields(frm) {
  const signed_fields = get_signed_fields();
  const prec2_fields = get_prec2_fields();
  function get_re(field) {
    if (signed_fields.includes(field)) {
      return /^(\+|-)?\d*\.?\d{0,2}$/;
    }
    if (field.includes('axis')) {
      return /^\d{0,3}$/;
    }
    if (field.includes('va')) {
      return /^[p0-9]*\/?[p0-9]*$/;
    }
    if (prec2_fields.includes(field)) {
      return /^\d*\.?\d{0,2}$/;
    }
    if (field.includes('pd')) {
      return /^\d*\.?\d{0,1}$/;
    }
  }
  function scrub(field, value) {
    const re = get_re(field);
    if (re) {
      return re.test(value) ? value : frm.doc[field];
    }
    return value;
  }
  return function(field, value) {
    const scrubbed = scrub(field, value);
    frm.set_value(field, scrubbed);
    return scrubbed;
  };
}

function blur_fields(frm) {
  return async function(field, value) {
    if (field.includes('sph') || field.includes('add') || field.includes('cyl')) {
      // considers cases where the user might just enter '+' or '-', hence the + '.0'
      const fval = Math.round(parseFloat((value || '') + '.0') * 4) / 4;
      await frm.set_value(field, format(field, fval));
      update_detail_vue_props(frm);
    }
  };
}

function render_detail_vue(frm) {
  const { $wrapper } = frm.get_field('details_html');
  $wrapper.empty();
  const doc = Object.assign(
    get_all_rx_params().reduce((a, x) => Object.assign(a, { [x]: undefined }), {}),
    { pd_total: undefined },
    frm.doc
  );
  return new Vue({
    el: $wrapper.html('<div />').children()[0],
    data: { doc },
    render: function(h) {
      return h(PrescriptionForm, {
        props: {
          doc: this.doc,
          update: update_fields(frm),
          fields: frm.fields_dict,
          blur: blur_fields(frm),
        },
      });
    },
  });
}

function update_detail_vue_props(frm) {
  if (frm.detail_vue) {
    frm.detail_vue.doc = Object.assign(frm.detail_vue.doc, frm.doc);
  }
}

function setup_route_back(frm) {
  if (frappe._from_link && frappe._from_link.frm) {
    const { doctype, docname } = frappe._from_link.frm;
    // disable native route back for save events. will handle submits by own
    frappe._from_link.frm = null;
    return ['Form', doctype, docname];
  }
  return null;
}

function set_expiry_date(frm) {
  frm.set_value('expiry_date', frappe.datetime.add_months(frm.doc.test_date, 6));
}

export default {
  setup: async function(frm) {
    const { message: settings = {} } = await frappe.db.get_value(
      'Optical Store Settings',
      null,
      'prescription_entry'
    );
    toggle_detail_entry(frm, settings.prescription_entry === 'ERPNext');
  },
  onload: function(frm) {
    frm.route_back = setup_route_back(frm);
  },
  refresh: function(frm) {
    frm.detail_vue = render_detail_vue(frm);
    if (frm.doc.__islocal) {
      set_expiry_date(frm);
    }
  },
  test_date: set_expiry_date,
  on_submit: async function(frm) {
    if (frm.route_back) {
      await frappe.set_route(frm.route_back);
      if (frappe._from_link_scrollY) {
        frappe.utils.scroll_to(frappe._from_link_scrollY);
      }
    }
  },
  type: update_detail_vue_props,
  add_right: async function(frm) {
    await Promise.all([
      handle_reading('right')(frm),
      frm.set_value('add_left', frm.doc.add_right),
    ]);
    update_detail_vue_props(frm);
  },
  add_left: async function(frm) {
    await handle_reading('left')(frm);
    update_detail_vue_props(frm);
  },
  pd_right: async function(frm) {
    await calc_total_pd(frm);
    update_detail_vue_props(frm);
  },
  pd_left: async function(frm) {
    await calc_total_pd(frm);
    update_detail_vue_props(frm);
  },
};
