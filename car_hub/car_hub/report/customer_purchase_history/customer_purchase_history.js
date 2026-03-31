frappe.query_reports["Customer Purchase History"] = {
    "filters": [
        {
            "fieldname": "customer",
            "label": "Customer",
            "fieldtype": "Link",
            "options": "Customer",
            "reqd": 1
        }
    ]
};