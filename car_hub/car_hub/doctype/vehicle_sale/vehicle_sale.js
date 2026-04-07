// Copyright (c) 2026, Dhanaa Lakshmi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle Sale', {

    onload: function(frm) {

        // Vehicle filter
        frm.set_query("vehicle", function() {
            return {
                filters: {
                    status: ["in", ["Available for Sale", "Reserved"]]
                }
            };
        });

        // Sales consultant filter
        frm.set_query("sales_consultant", function() {
            return {
                query: "frappe.core.doctype.user.user.user_query",
                filters: {
                    role: "Sales Consultant"
                }
            };
        });
    },

    selling_price: calculate_totals,
    transfer_fee: calculate_totals,
    insurance_charges: calculate_totals,
    discount: calculate_totals
});

function calculate_totals(frm) {
    let subtotal = (frm.doc.selling_price || 0)
        + (frm.doc.documentation_charges || 0)
        + (frm.doc.transfer_fee || 0)
        + (frm.doc.insurance_charges || 0)
        + (frm.doc.accessories_total || 0);

    frm.set_value("subtotal", subtotal);
}

frappe.ui.form.on('Vehicle Accessories', {
    quantity: function(frm, cdt, cdn) {
        calculate_accessory_total(frm, cdt, cdn);
    },
    unit_price: function(frm, cdt, cdn) {
        calculate_accessory_total(frm, cdt, cdn);
    }
});

function calculate_accessory_total(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    row.total_amount = (row.quantity || 0) * (row.unit_price || 0);
    
    frm.refresh_field('accessories');

    // Update overall accessories total
    let total = 0;
    frm.doc.accessories.forEach(r => {
        total += r.total_amount || 0;
    });
    frm.set_value('accessories_total', total);
}
