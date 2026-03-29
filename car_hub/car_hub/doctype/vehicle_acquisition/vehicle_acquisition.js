// Copyright (c) 2026, Dhanaa Lakshmi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle Acquisition', {

    refresh: function(frm) {
        calculate_totals(frm);
    },

    transportation_charges: calculate_totals,
    documentation_fees: calculate_totals,
    advance_paid: calculate_totals,
    tax_percentage: calculate_totals,

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

    let tax = (total * (frm.doc.tax_percentage || 0)) / 100;
    frm.set_value("tax_amount", tax);

    let grand = total
        + (frm.doc.transportation_charges || 0)
        + (frm.doc.documentation_fees || 0)
        + tax
        - (frm.doc.advance_paid || 0);

    frm.set_value("grand_total", grand);
}
