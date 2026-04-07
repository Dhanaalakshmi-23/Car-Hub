import frappe

def execute(filters=None):

    columns = [
        {"label": "Vehicle (Reg No)", "fieldname": "registration_number", "fieldtype": "Data", "width": 150},
        {"label": "Manufacturer", "fieldname": "manufacturer", "fieldtype": "Data", "width": 150},
        {"label": "Model", "fieldname": "model", "fieldtype": "Data", "width": 120},
        {"label": "Classification", "fieldname": "classification", "fieldtype": "Data", "width": 150},
        {"label": "Days in Stock", "fieldname": "days_in_stock", "fieldtype": "Int", "width": 130},
        {"label": "Acquisition Cost", "fieldname": "acquisition_cost", "fieldtype": "Currency", "width": 150},
        {"label": "Expected Selling Price", "fieldname": "expected_price", "fieldtype": "Currency", "width": 180},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]

    query = """
        SELECT
            vi.registration_number,
            vi.manufacturer,
            vi.model,
            vc.name AS classification,

            DATEDIFF(CURDATE(), va.acquisition_date) AS days_in_stock,

            va.total_purchase_cost AS acquisition_cost,
            vi.expected_selling_price AS expected_price,
            vi.status

        FROM `tabVehicle Inventory` vi

        LEFT JOIN `tabVehicle Acquisition` va 
            ON vi.vehicle_acquisition = va.name

        LEFT JOIN `tabVehicle Classification` vc 
            ON vi.vehicle_classification = vc.name

        WHERE vi.status != 'Sold'

        ORDER BY days_in_stock DESC
    """

    data = frappe.db.sql(query, as_dict=True)

    return columns, data