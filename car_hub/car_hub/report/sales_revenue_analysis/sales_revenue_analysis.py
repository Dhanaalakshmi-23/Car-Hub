import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)

    return columns, data, None, chart


def get_columns():
    return [
        {"label": "Vehicle Classification", "fieldname": "classification", "fieldtype": "Data", "width": 200},
        {"label": "Vehicles Sold", "fieldname": "count", "fieldtype": "Int", "width": 120},
        {"label": "Total Revenue", "fieldname": "revenue", "fieldtype": "Currency", "width": 150},
        {"label": "Total Profit", "fieldname": "profit", "fieldtype": "Currency", "width": 150},
        {"label": "Avg Profit %", "fieldname": "avg_profit", "fieldtype": "Percent", "width": 120},
    ]


def get_data(filters):
    conditions = ""

    if filters.get("from_date"):
        conditions += " AND vs.posting_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND vs.posting_date <= %(to_date)s"
    if filters.get("sales_consultant"):
        conditions += " AND vs.sales_consultant = %(sales_consultant)s"

    query = f"""
        SELECT
            vc.name AS classification,
            COUNT(vs.name) AS count,
            SUM(vs.selling_price) AS revenue,
            SUM(vs.profit) AS profit,
            AVG(vs.profit_margin) AS avg_profit

        FROM `tabVehicle Sale` vs

        JOIN `tabVehicle Inventory` vi
            ON vs.vehicle = vi.name

        JOIN `tabVehicle Classification` vc
            ON vi.vehicle_classification = vc.name

        WHERE vs.docstatus = 1
        {conditions}

        GROUP BY vc.name
    """

    return frappe.db.sql(query, filters, as_dict=True)


def get_chart(data):
    labels = [d.classification for d in data]
    values = [d.revenue for d in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Revenue",
                    "values": values
                }
            ]
        },
        "type": "bar"
    }