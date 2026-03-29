// Copyright (c) 2026, Dhanaa Lakshmi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Seller Registry', {

    phone_number: function(frm) {
        if (frm.doc.phone_number && !/^[0-9]{10}$/.test(frm.doc.phone_number)) {
            frappe.msgprint("Phone number must be 10 digits");
            frm.set_value("phone_number", "");
        }
    },

    email_address: function(frm) {
        if (frm.doc.email_address && !/^[^@]+@[^@]+\.[^@]+$/.test(frm.doc.email_address)) {
            frappe.msgprint("Invalid Email Address");
            frm.set_value("email_address", "");
        }
    },

    seller_type: function(frm) {
        if (frm.doc.seller_type === "Individual Owner") {
            frm.set_df_property("id_proof_type", "reqd", 1);
            frm.set_df_property("id_proof_number", "reqd", 1);
        } else {
            frm.set_df_property("id_proof_type", "reqd", 0);
            frm.set_df_property("id_proof_number", "reqd", 0);
        }
    }
});
