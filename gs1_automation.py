import requests
import xlwings as xw
with xw.App(visible=False) as app:
    # Open the workbook via the app instance
    wb = xw.Book("GS1_Product_Import_Full_Test_1.xlsx")
    sheet = wb.sheets["Produktangaben"] # Update to your sheet name

    try:
        target_col = 36  # AJ
        header_row = 3
        data_start_row = 4

        # 1. Logic to find the last row
        last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row

        # 2. Delete rows (backward loop)
        for i in range(last_row, data_start_row - 1, -1):
            if sheet.range(i, target_col).value is not False or sheet.range(i, 1).value is None:
                sheet.api.Rows(i).Delete()

        # 3. Re-calculate and Fix Column A
        new_last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row
        if new_last_row >= data_start_row:
            target_range = sheet.range(f"A{data_start_row}:A{new_last_row}")
            target_range.number_format = "@" # Force Text
            
            # Clean and re-write values as pure strings
            vals = target_range.value
            if isinstance(vals, list):
                clean = [[str(int(x)) if isinstance(x, (int, float)) else str(x).strip()] for x in vals]
                target_range.value = clean
            else:
                target_range.value = str(int(vals)) if isinstance(vals, (int, float)) else str(vals).strip()

        wb.save("final_api_ready.xlsx")
        print("File processed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Closing the book is handled by 'with', but being explicit helps
        wb.close()

import requests
gs1_token = "eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJodHRwczovL3Byb2Quc2ltYmEuZWVjYy5kZS90ZXN0Iiwic3ViIjoiMzEwNzEzIiwiaWF0IjoxNzc0MzUxODI1LCJleHAiOjQ5Mjc5NTE4MjUsInBlcm1pc3Npb25zIjoiRVBTLEdUSU5NQU5BR0VSLFZCR0YsR0xOTUFOQUdFUixHUzFDT01QTEVURSIsImdsbiI6IjQyNTA0MDk3MDAwMDEiLCJuYW1lIjoiRGFuaWVsIER1YnMiLCJjb21wYW55IjoiU2VkYXRlY2ggRXVyb3BlIEdtYkgiLCJsYW5ndWFnZSI6IkRFIiwicHJldmlvdXNfZ2xuIjoiIiwicHJldmlvdXNfY29nbG5BY2NvdW50SWQiOiIiLCJlbWFpbCI6ImluZm9Ac2VkYXRlY2guZXUiLCJjb2dsbkFjY291bnRJZCI6IkQyNTA4MDcifQ.6U9hg0I_DX0JJ99kiJHYs_I-_1bSD6iOBvxbWSkHBADTtqjyKx176PhniY2lS6GYWJwmjEff0TQSSq9PQ_QikA"
headers = {
    'Authorization': f'Bearer {gs1_token}',
    'Accept': '*/*',
}
url = "https://serviceplattform.gs1.de/api/master_data_service/v1/product/import"
with open("final_api_ready.xlsx", "rb") as file:
    response = requests.post(url, headers = headers, files = {'file': file})