// Copyright (c) 2026, Dhanaa Lakshmi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle Evaluation Task', {
    onload: function(frm) {
        if (!frm.doc.due_date) {
            let d = frappe.datetime.add_days(frappe.datetime.nowdate(), 3);
            frm.set_value("due_date", d);
        }
    },

    started_on: function(frm) {
        calculate_duration(frm);
        if (frm.doc.started_on && frm.doc.status === "Pending") {
            frm.set_value("status", "In Progress");
        }
    },

    completed_on: function(frm) {
        calculate_duration(frm);
        if (frm.doc.started_on && frm.doc.status === "Pending") {
            frm.set_value("status", "In Progress");
        }
    },
    recommended_price: calculate_profit,
    refurbishment_cost: calculate_profit
});

function calculate_duration(frm) {

    if (frm.doc.started_on && frm.doc.completed_on) {

        let start = frappe.datetime.str_to_obj(frm.doc.started_on);
        let end = frappe.datetime.str_to_obj(frm.doc.completed_on);

        let diff_ms = end - start;
        let diff_hrs = diff_ms / (1000 * 60 * 60);

        frm.set_value('evaluation_duration', diff_hrs.toFixed(2));
    }
}
function calculate_profit(frm) {

    if (!frm.doc.vehicle_inventory) return;

    frappe.db.get_value("Vehicle Inventory", frm.doc.vehicle_inventory, "acquisition_cost")
        .then(r => {

            let cost = r.message.acquisition_cost || 0;
            let refurb = frm.doc.refurbishment_cost || 0;
            let price = frm.doc.recommended_price || 0;

            let profit = price - (cost + refurb);

            frm.set_value("expected_profit", profit);
        });
}
