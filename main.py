import gspread
from oauth2client.service_account import ServiceAccountCredentials

def append_to_google_sheet(data_dict):
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Authenticate
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
    client = gspread.authorize(creds)
    
    # Open the sheet by name
    sheet = client.open("SolarCalculatorData").sheet1  # Must match the Google Sheet title

    # Prepare the row
    row = [
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

    # Append the row
    sheet.append_row(row)

