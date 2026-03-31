import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    summary = get_summary(data, filters)

    return columns, data, None, None, summary


def get_columns():
    return [
        {"label": "Vehicle", "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle Inventory", "width": 180},
        {"label": "Manufacturer", "fieldname": "manufacturer", "fieldtype": "Data", "width": 140},
        {"label": "Model", "fieldname": "model", "fieldtype": "Data", "width": 120},
        {"label": "Sale Date", "fieldname": "date", "fieldtype": "Date", "width": 120},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 130},
        {"label": "Profit", "fieldname": "profit", "fieldtype": "Currency", "width": 130},
    ]


def get_data(filters):
    return frappe.db.sql("""
        SELECT
            vs.vehicle,
            vi.manufacturer,
            vi.model,
            vs.posting_date AS date,
            vs.selling_price AS amount,
            vs.profit

        FROM `tabVehicle Sale` vs

        JOIN `tabVehicle Inventory` vi
            ON vs.vehicle = vi.name

        WHERE vs.customer = %(customer)s
        AND vs.docstatus = 1
    """, filters, as_dict=True)


def get_summary(data, filters):

    total_spent = sum(d.amount for d in data)
    total_profit = sum(d.profit for d in data)
    total_purchases = len(data)

    # Referral Bonus (from Customer doctype)
    referral_bonus = frappe.db.get_value(
        "Customer",
        filters.get("customer"),
        "referral_bonus"
    ) or 0

    # Consulting Engagement Count
    engagements = frappe.db.count(
        "Consulting Engagement",
        {"customer": filters.get("customer")}
    )

    return [
        {"label": "Total Purchases", "value": total_purchases, "indicator": "Blue"},
        {"label": "Total Spent", "value": total_spent, "indicator": "Green"},
        {"label": "Total Profit", "value": total_profit, "indicator": "Orange"},
        {"label": "Referral Bonus", "value": referral_bonus, "indicator": "Purple"},
        {"label": "Consulting Engagements", "value": engagements, "indicator": "Red"},
    ]