import requests

import xlwings as xw

app = xw.App(visible=False)
wb = xw.Book("GS1_Product_Import_Full_Test_1.xlsx")
sheet = wb.sheets["Produktangaben"]

target_col = 36 
header_row = 3   
data_start_row = 4 

last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row

for i in range(last_row, data_start_row - 1, -1):
    val_aj = sheet.range(i, target_col).value
    val_a = sheet.range(i, 1).value

    if val_aj is not False or val_a is None:
        sheet.api.Rows(i).Delete()


new_last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row


if new_last_row >= data_start_row:
    target_range = sheet.range(f"A{data_start_row}:A{new_last_row}")
    target_range.number_format = "@" 
    
    current_values = target_range.value
    
    if isinstance(current_values, list):
        formatted = [[str(int(x)).strip() if isinstance(x, (int, float)) else str(x).strip()] for x in current_values]
    else:
        formatted = str(int(current_values)).strip() if isinstance(current_values, (int, float)) else str(current_values).strip()
    
    target_range.value = formatted

wb.save("final_api_ready_1.xlsx")
wb.close()
app.quit()

import requests
gs1_token = "eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJodHRwczovL3Byb2Quc2ltYmEuZWVjYy5kZS90ZXN0Iiwic3ViIjoiMzEwNzEzIiwiaWF0IjoxNzc0MzUxODI1LCJleHAiOjQ5Mjc5NTE4MjUsInBlcm1pc3Npb25zIjoiRVBTLEdUSU5NQU5BR0VSLFZCR0YsR0xOTUFOQUdFUixHUzFDT01QTEVURSIsImdsbiI6IjQyNTA0MDk3MDAwMDEiLCJuYW1lIjoiRGFuaWVsIER1YnMiLCJjb21wYW55IjoiU2VkYXRlY2ggRXVyb3BlIEdtYkgiLCJsYW5ndWFnZSI6IkRFIiwicHJldmlvdXNfZ2xuIjoiIiwicHJldmlvdXNfY29nbG5BY2NvdW50SWQiOiIiLCJlbWFpbCI6ImluZm9Ac2VkYXRlY2guZXUiLCJjb2dsbkFjY291bnRJZCI6IkQyNTA4MDcifQ.6U9hg0I_DX0JJ99kiJHYs_I-_1bSD6iOBvxbWSkHBADTtqjyKx176PhniY2lS6GYWJwmjEff0TQSSq9PQ_QikA"
headers = {
    'Authorization': f'Bearer {gs1_token}',
    'Accept': '*/*',
}
url = "https://serviceplattform.gs1.de/api/master_data_service/v1/product/import"
with open("final_api_ready_1.xlsx", "rb") as file:
    response = requests.post(url, headers = headers, files = {'file': file})