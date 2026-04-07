frappe.query_reports["Inventory Aging Report"] = {
    formatter: function(value, row, column, data, default_formatter) {

        // Apply default formatting
        value = default_formatter(value, row, column, data);

        // Highlight entire row if > 45 days
        if (data && data.days_in_stock > 45) {
            value = `<span style="color:red; font-weight:bold">${value}</span>`;
        }

        return value;
    }
};