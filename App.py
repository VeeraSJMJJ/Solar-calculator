from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from io import BytesIO
from xhtml2pdf import pisa
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calculator.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
class Calculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    location = db.Column(db.String(100))
    category = db.Column(db.String(50))
    billing_cycle = db.Column(db.String(20))
    units = db.Column(db.Float)
    tariff = db.Column(db.Float)
    monthly_bill = db.Column(db.Float)
    system_size = db.Column(db.Float)
    estimated_cost = db.Column(db.Float)
    subsidy = db.Column(db.Float)
    net_cost = db.Column(db.Float)
    monthly_savings = db.Column(db.Float)
    annual_savings = db.Column(db.Float)
    payback_years = db.Column(db.Float)

with app.app_context():
    db.create_all()

# Constants
TARIFFS = {
    "Residential": 5.5,
    "Commercial": 8.10,
    "Industrial": 9.50
}
COST_PER_KW = 65000  # Installation cost per kW

# Google Sheets append
def append_to_google_sheet(data_dict):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("SolarCalculatorData").sheet1

    row = [
        data_dict["name"],
        data_dict["phone"],
        data_dict["email"],
        data_dict["location"],
        data_dict["category"],
        data_dict["billing_cycle"],
        data_dict["units"],
        data_dict["tariff"],
        data_dict["monthly_bill"],
        data_dict["system_size"],
        data_dict["estimated_cost"],
        data_dict["subsidy"],
        data_dict["net_cost"],
        data_dict["monthly_savings"],
        data_dict["annual_savings"],
        data_dict["payback_years"]
    ]
    sheet.append_row(row)

# Main route
@app.route("/", methods=["GET", "POST"])
def calculator():
    result = None
    if request.method == "POST":
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        location = request.form.get('location', '')
        category = request.form['category']
        billing_cycle = request.form['billing_cycle']
        units = float(request.form['units'])
        tariff = float(request.form.get('tariff') or TARIFFS[category])
        monthly_bill = float(request.form['monthly_bill'])

        multiplier = 0.5 if billing_cycle == "Bi-monthly" else 1
        monthly_units = units * multiplier
        system_size = round(monthly_units / 120, 2)
        estimated_cost = system_size * COST_PER_KW

        if category == "Residential":
            if system_size <= 3:
                subsidy = system_size * 14588
            elif system_size <= 10:
                subsidy = 3 * 14588 + (system_size - 3) * 7294
            else:
                subsidy = 0
        else:
            subsidy = 0

        net_cost = estimated_cost - subsidy
        monthly_savings = monthly_units * tariff
        annual_savings = monthly_savings * 12
        payback_years = round(net_cost / annual_savings, 2) if annual_savings else 0

        calc = Calculation(
            name=name,
            phone=phone,
            email=email,
            location=location,
            category=category,
            billing_cycle=billing_cycle,
            units=units,
            tariff=tariff,
            monthly_bill=monthly_bill,
            system_size=system_size,
            estimated_cost=estimated_cost,
            subsidy=subsidy,
            net_cost=net_cost,
            monthly_savings=monthly_savings,
            annual_savings=annual_savings,
            payback_years=payback_years
        )
        db.session.add(calc)
        db.session.commit()

        data_dict = {
            "name": name,
            "phone": phone,
            "email": email,
            "location": location,
            "category": category,
            "billing_cycle": billing_cycle,
            "units": units,
            "tariff": tariff,
            "monthly_bill": monthly_bill,
            "system_size": system_size,
            "estimated_cost": estimated_cost,
            "subsidy": subsidy,
            "net_cost": net_cost,
            "monthly_savings": monthly_savings,
            "annual_savings": annual_savings,
            "payback_years": payback_years
        }
        append_to_google_sheet(data_dict)

        result = {
            "system_size": system_size,
            "estimated_cost": estimated_cost,
            "subsidy": subsidy,
            "net_cost": net_cost,
            "monthly_savings": monthly_savings,
            "annual_savings": annual_savings,
            "payback_years": payback_years
        }

    return render_template("calculator.html", result=result, tariffs=TARIFFS)

# Export to Excel
@app.route("/export-excel", methods=["POST"])
def export_excel():
    form_data = request.form
    data = {
        "Category": [form_data["category"]],
        "Billing Cycle": [form_data["billing_cycle"]],
        "Units": [form_data["units"]],
        "Tariff (₹/unit)": [form_data["tariff"]],
        "Monthly Bill (₹)": [form_data["monthly_bill"]],
        "System Size (kW)": [form_data["system_size"]],
        "Estimated Cost (₹)": [form_data["estimated_cost"]],
        "Subsidy (₹)": [form_data["subsidy"]],
        "Net Cost (₹)": [form_data["net_cost"]],
        "Monthly Savings (₹)": [form_data["monthly_savings"]],
        "Annual Savings (₹)": [form_data["annual_savings"]],
        "Payback Years": [form_data["payback_years"]]
    }
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Solar Report')
    output.seek(0)
    return send_file(output, download_name="Solar_Report.xlsx", as_attachment=True)

# ✅ Run on dynamic port for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Must be inside /templates folder

if __name__ == '__main__':
    app.run(debug=True)
