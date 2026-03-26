// Copyright (c) 2026, Dhanaa Lakshmi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Consulting Engagement', {
    onload: function(frm) {
        frm.set_query("consultant", function() {
            return {
                query: "frappe.core.doctype.user.user.user_query",
                filters: {
                    role: "Consultant"
                }
            };
        });
    }
});
