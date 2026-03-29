// Copyright (c) 2026, Dhanaa Lakshmi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle Inventory', {

    acquisition_cost: calculate_total,
    refurbishment_cost: calculate_total,

    expected_selling_price: validate_price,
    minimum_price: validate_price,

    odometerkm: function(frm) {
        if (frm.doc.odometerkm < 0) {
            frappe.msgprint("Odometer cannot be negative");
            frm.set_value("odometerkm", "");
        }
    }
});


function calculate_total(frm) {
    let total = (frm.doc.acquisition_cost || 0) + (frm.doc.refurbishment_cost || 0);
    frm.set_value("total_investment", total);
}


function validate_price(frm) {
    if (frm.doc.minimum_price > frm.doc.expected_selling_price) {
        frappe.msgprint("Minimum price cannot exceed expected selling price");
        frm.set_value("minimum_price", "");
    }
}