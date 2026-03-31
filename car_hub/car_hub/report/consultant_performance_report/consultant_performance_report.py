import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)

    return columns, data, None, chart


def get_columns():
    return [
        {"label": "Consultant", "fieldname": "consultant", "fieldtype": "Data", "width": 200},
        {"label": "Closed Deals", "fieldname": "deals", "fieldtype": "Int", "width": 120},
        {"label": "Total Revenue", "fieldname": "revenue", "fieldtype": "Currency", "width": 150},
        {"label": "Avg Profit %", "fieldname": "avg_profit", "fieldtype": "Percent", "width": 120},
        {"label": "Engagements", "fieldname": "engagements", "fieldtype": "Int", "width": 120},
    ]


def get_data(filters):
    conditions = ""

    if filters.get("from_date"):
        conditions += " AND vs.posting_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND vs.posting_date <= %(to_date)s"
    if filters.get("consultant"):
        conditions += " AND vs.sales_consultant = %(consultant)s"

    query = f"""
        SELECT
            vs.sales_consultant AS consultant,
            COUNT(vs.name) AS deals,
            SUM(vs.selling_price) AS revenue,
            AVG(vs.profit_margin) AS avg_profit,

            (
                SELECT COUNT(ce.name)
                FROM `tabConsulting Engagement` ce
                WHERE ce.consultant = vs.sales_consultant
            ) AS engagements

        FROM `tabVehicle Sale` vs

        JOIN `tabVehicle Inventory` vi
            ON vs.vehicle = vi.name

        WHERE vs.docstatus = 1
        {conditions}

        GROUP BY vs.sales_consultant
    """

    return frappe.db.sql(query, filters, as_dict=True)


def get_chart(data):
    labels = [d.consultant for d in data]
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