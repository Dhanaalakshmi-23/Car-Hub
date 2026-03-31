// Copyright (c) 2026, Dhanaa Lakshmi and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Revenue Analysis"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "sales_consultant",
            "label": "Sales Consultant",
            "fieldtype": "Link",
            "options": "User"
        }
    ]
};
