import frappe
from frappe.utils import today, add_days

# SCHEDULED 1: Every Monday 8 AM
def send_slow_inventory_report():
    """Email Sales Managers: vehicles in 'Available for Sale' > 30 days."""
    slow_vehicles = frappe.db.sql("""
        SELECT
            vi.registration_number,
            vi.manufacturer,
            vi.model,
            vi.year_of_manufacture,
            vi.expected_selling_price,
            DATEDIFF(CURDATE(), vi.acquisition_date) AS days_in_stock
        FROM `tabVehicle Inventory` vi
        WHERE vi.status = 'Available for Sale'
          AND DATEDIFF(CURDATE(), vi.acquisition_date) > 30
        ORDER BY days_in_stock DESC
    """, as_dict=True)

    if not slow_vehicles:
        return

    rows = "".join([
        f"<tr>"
        f"<td>{v.registration_number}</td>"
        f"<td>{v.manufacturer} {v.model} ({v.year_of_manufacture})</td>"
        f"<td>₹{(v.expected_selling_price or 0):,.0f}</td>"
        f"<td style='color:red;font-weight:bold'>{v.days_in_stock} days</td>"
        f"</tr>"
        for v in slow_vehicles
    ])

    body = f"""
<h2 style="color:#1a3c6e;">Slow-Moving Inventory Report</h2>
<p>Vehicles in <b>Available for Sale</b> status for more than <b>30 days</b>:</p>
<table border="1" cellpadding="8" cellspacing="0"
       style="border-collapse:collapse;width:100%;font-size:13px;">
  <thead style="background:#1a3c6e;color:white;">
    <tr>
      <th>Reg No</th><th>Vehicle</th><th>Expected Price</th><th>Days in Stock</th>
    </tr>
  </thead>
  <tbody>{rows}</tbody>
</table>
<p>Total: <b>{len(slow_vehicles)}</b> slow-moving vehicles as of {today()}</p>
"""

    managers = frappe.get_all(
        "Has Role",
        filters={"role": "Sales Manager", "parenttype": "User"},
        fields=["parent"],
    )
    for m in managers:
        email = frappe.db.get_value("User", m.parent, "email")
        if email:
            frappe.sendmail(
                recipients=[email],
                subject=f"[Car Hub] Weekly Slow-Moving Inventory — {len(slow_vehicles)} vehicles",
                message=body,
            )


# SCHEDULED 2: Daily at 6 PM 
def auto_close_delivered_sales():
    """Auto-close Vehicle Sales in 'Delivered' status for more than 15 days."""
    sales = frappe.db.sql("""
        SELECT name
        FROM `tabVehicle Sale`
        WHERE status = 'Delivered'
          AND delivery_date IS NOT NULL
          AND DATEDIFF(CURDATE(), delivery_date) > 15
          AND docstatus = 1
    """, as_dict=True)

    count = 0
    for sale in sales:
        try:
            frappe.db.set_value("Vehicle Sale", sale.name, "status", "Closed")
            count += 1
        except Exception as e:
            frappe.log_error(str(e), f"[Car Hub] Auto-close failed: {sale.name}")

    if count:
        frappe.db.commit()
        frappe.logger().info(f"[Car Hub] Auto-closed {count} delivered sales.")


# SCHEDULED 3: Daily at 9 AM
def log_overdue_evaluations():
    """Log evaluation tasks that have been pending/in-progress for more than 5 days."""
    overdue = frappe.db.sql("""
        SELECT
            name,
            vehicle_inventory,
            evaluator,
            evaluation_date,
            DATEDIFF(CURDATE(), evaluation_date) AS days_pending
        FROM `tabVehicle Evaluation Task`
        WHERE status IN ('Pending', 'In Progress')
          AND DATEDIFF(CURDATE(), evaluation_date) > 5
        ORDER BY days_pending DESC
    """, as_dict=True)

    if not overdue:
        return

    summary = "\n".join([
        f"Task: {t.name} | Vehicle: {t.vehicle_inventory} "
        f"| Evaluator: {t.evaluator} | Days Pending: {t.days_pending}"
        for t in overdue
    ])

    frappe.log_error(
        title=f"[Car Hub] {len(overdue)} Overdue Evaluation Tasks — {today()}",
        message=f"Evaluation tasks pending > 5 days:\n\n{summary}",
    )

