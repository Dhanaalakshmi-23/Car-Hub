// Copyright (c) 2026, Dhanaa Lakshmi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle Acquisition', {
        before_cancel: function(frm) {

        return new Promise((resolve, reject) => {

            let d = new frappe.ui.Dialog({
                title: 'Enter Cancellation Reason',
                fields: [
                    {
                        label: 'Reason',
                        fieldname: 'reason',
                        fieldtype: 'Small Text',
                        reqd: 1
                    }
                ],
                primary_action_label: 'Submit',
                primary_action(values) {

                    // set value to doc
                    frm.set_value('cancellation_reason', values.reason);

                    d.hide();
                    resolve();  // allow cancel
                }
            });

            d.show();
        });
    },

    refresh: function(frm) {
        calculate_totals(frm);
        if (frm.doc.docstatus === 0 && frm.doc.status === "Draft") {
            frm.add_custom_button('Send for Approval', () => {
                frm.set_value('status', 'Pending Approval');
                frm.save();
            });
        }

        if (frm.doc.status === "Pending Approval") {
            frm.add_custom_button('Approve', () => {
                frm.set_value('status', 'Approved');
                frm.save();
            });
        }
        if (frm.doc.status === "Rejected") {
            frm.disable_save();
            frm.disable_submit();
        }
        if (frm.doc.status === "Pending Approval") {
            frm.add_custom_button('Reject', () => {
                frm.set_value('status', 'Rejected');
                frm.save();
            });
        }
    },
    transportation_km: function(frm) {
        frm.call('calculate_totals').then(() => {
            frm.refresh_fields([
                'transportation_charges',
                'grand_total',
                'total_purchase_cost'
            ]);
        });
    },
    documentation_fees: calculate_totals,
    advance_paid: calculate_totals,

});

frappe.ui.form.on('Vehicle Acquisition Item', {

    purchase_price: function(frm, cdt, cdn) {
        calculate_totals(frm);
    },

    registration_number: function(frm, cdt, cdn) {
        let rows = frm.doc.vehicles || [];
        let reg_numbers = rows.map(r => r.registration_number);

        let duplicates = reg_numbers.filter((item, index) => reg_numbers.indexOf(item) !== index);

        if (duplicates.length > 0) {
            frappe.msgprint("Duplicate Registration Number not allowed");
            frappe.model.set_value(cdt, cdn, "registration_number", "");
        }
    }
});


function calculate_totals(frm) {

    let total = 0;

    (frm.doc.vehicles || []).forEach(v => {
        total += v.purchase_price || 0;
    });

    frm.set_value("total_purchase_cost", total);


    let grand = total
        + (frm.doc.transportation_charges || 0)
        + (frm.doc.documentation_fees || 0)
        - (frm.doc.advance_paid || 0);

    frm.set_value("grand_total", grand);
}
