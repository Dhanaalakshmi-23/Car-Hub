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
    conditions = []
    values = {}

    if filters.get("from_date"):
        conditions.append("vs.sale_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("vs.sale_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    # if filters.get("sales_consultant"):
    #     conditions.append("vs.sales_consultant = %(sales_consultant)s")
    #     values["sales_consultant"] = filters.get("sales_consultant")

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = " AND " + where_clause

    query = f"""
            SELECT
                vc.name AS classification,
                COUNT(vs.name) AS count,
                SUM(vs.selling_price) AS revenue,
                SUM(vs.selling_price - IFNULL(va.total_purchase_cost, 0)) AS profit,
                AVG(
                    CASE 
                        WHEN vs.selling_price > 0 
                        THEN ((vs.selling_price - IFNULL(va.total_purchase_cost, 0)) / vs.selling_price) * 100
                        ELSE 0 
                    END
                ) AS avg_profit
            FROM `tabVehicle Sale` vs
            LEFT JOIN `tabVehicle Inventory` vi ON vs.vehicle = vi.name
            LEFT JOIN `tabVehicle Acquisition` va ON vi.vehicle_acquisition = va.name
            LEFT JOIN `tabVehicle Classification` vc ON vi.vehicle_classification = vc.name
            WHERE vs.docstatus = 1
            {where_clause}
            GROUP BY vc.name
        """

    return frappe.db.sql(query, values, as_dict=True)

def get_chart(data):
    return {
        "data": {
            "labels": [d.classification for d in data],
            "datasets": [
                {
                    "name": "Revenue",
                    "values": [d.revenue for d in data]
                }
            ]
        },
        "type": "bar"
    }