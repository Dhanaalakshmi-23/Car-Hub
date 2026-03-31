// Copyright (c) 2026, Dhanaa Lakshmi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Registry', {

    refresh: function(frm) {
        toggle_fields(frm);

        if (!frm.is_new()) {
            frm.add_custom_button("Purchase History", function() {
                frappe.set_route("query-report", "Customer Purchase History", {
                    customer: frm.doc.name
                });
            });
        }
    
    },

    customer_type: function(frm) {
        toggle_fields(frm);
    },

    referral_source: function(frm) {
        toggle_referral(frm);
    }
});


function toggle_fields(frm) {
    if (frm.doc.customer_type !== "Individual") {
        frm.set_df_property("company_name", "reqd", 1);
        frm.set_df_property("gst_number", "reqd", 1);
    } else {
        frm.set_df_property("company_name", "reqd", 0);
        frm.set_df_property("gst_number", "reqd", 0);
    }
}

function toggle_referral(frm) {
    if (frm.doc.referral_source === "Referred by Existing Customer") {
        frm.set_df_property("referred_by", "reqd", 1);
    } else {
        frm.set_df_property("referred_by", "reqd", 0);
    }
}
