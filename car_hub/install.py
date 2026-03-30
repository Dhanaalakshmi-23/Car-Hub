import frappe
from frappe import _


def after_install():
    create_roles()
    create_default_settings()
    create_vehicle_classifications()
    create_sample_manufacturers()
    frappe.db.commit()
    frappe.msgprint(_("Car Hub installed successfully!"), alert=True)

def create_roles():
    roles = [
        "Sales Consultant",
        "Sales Manager",
        "Evaluator",
        "Acquisition Manager",
        "Dealership Admin",
    ]
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role}).insert(ignore_permissions=True)
    print("Roles created")


def create_default_settings():
    if frappe.db.exists("Dealership Settings", "Dealership Settings"):
        return
    settings = frappe.get_single("Dealership Settings")
    settings.dealership_name = "Car Hub"
    settings.address = "Car Hub Pvt Ltd,Main Road,Coimbatore, Tamil Nadu,India - 600001"
    settings.default_currency = "INR"
    settings.tax_percentage = 18.0
    settings.from_email = "dhanaalakshminarayanan@gmail.com"
    settings.default_documentation_charges = 3000
    settings.transfer_fee = 5000
    settings.minimum_profit_margin = 10
    settings.max_discount_percent = 5
    settings.warranty_days = 180
    settings.enable_referral = 1
    settings.referral_bonus_amount = 2000
    settings.auto_create_evaluation_task = 1
    settings.save(ignore_permissions=True)
    print("Default settings created")

def create_vehicle_classifications():
    classifications = [
        # (name, parent, is_group, avg_min, avg_max, depreciation, popularity, high_demand)
        ("Passenger Vehicles",  None,                   1, 0,        0,        0,    0, 0),
        ("Sedan",               "Passenger Vehicles",   1, 600000,   2000000,  12,   8, 1),
        ("Compact Sedan",       "Sedan",                0, 600000,   1000000,  14,   7, 1),
        ("Executive Sedan",     "Sedan",                0, 1000000,  2000000,  10,   6, 0),
        ("SUV",                 "Passenger Vehicles",   1, 800000,   4000000,  10,   9, 1),
        ("Compact SUV",         "SUV",                  0, 800000,   1800000,  11,   9, 1),
        ("Full-Size SUV",       "SUV",                  0, 1800000,  4000000,   9,   7, 0),
        ("Hatchback",           "Passenger Vehicles",   0, 300000,   900000,   15,   8, 1),
        ("MPV / Van",           "Passenger Vehicles",   0, 500000,   1500000,  13,   5, 0),
        ("Commercial Vehicles", None,                   1, 0,        0,         0,   0, 0),
        ("Pickup Truck",        "Commercial Vehicles",  0, 700000,   2000000,  12,   4, 0),
        ("Mini Truck",          "Commercial Vehicles",  0, 400000,   1000000,  14,   3, 0),
        ("Panel Van",           "Commercial Vehicles",  0, 500000,   1200000,  13,   3, 0),
        ("Luxury",              None,                   1, 0,        0,         0,   0, 0),
        ("Sports Car",          "Luxury",               0, 3000000, 15000000,   8,   4, 0),
        ("Premium SUV",         "Luxury",               0, 4000000, 12000000,   7,   5, 0),
    ]
    for name, parent, is_group, avg_min, avg_max, depr, pop, hd in classifications:
        if not frappe.db.exists("Vehicle Classification", name):
            doc = frappe.get_doc({
                "doctype": "Vehicle Classification",
                "classification_name": name,
                "parent_classification": parent,
                "is_group": is_group,
                "min_price": avg_min,
                "max_price": avg_max,
                "depreciation_rate": depr,
                "popularity_score": pop,
                "high_demand": hd,
                "is_active": 1,
            })
            doc.insert(ignore_permissions=True)
    print("Vehicle classifications created")

def create_sample_manufacturers():
    manufacturers = [
        "Maruti Suzuki", "Hyundai", "Tata Motors", "Mahindra", "Honda",
        "Toyota", "Ford", "Volkswagen", "Kia", "MG Motor",
        "BMW", "Mercedes-Benz", "Audi", "Jeep", "Skoda",
    ]
    for name in manufacturers:
        if not frappe.db.exists("Manufacturer", name):
            frappe.get_doc({
                "doctype": "Manufacturer",
                "manufacturer_name": name,
            }).insert(ignore_permissions=True)
    print("Sample manufacturers created")