import xlwt
from datetime import datetime

def write_sheet_title(sheet,result_data):
    column = 0
    row = 0
    for key in result_data.keys():
        sheet.write(row,column,key)
        column += 1

def write_sheet_data(sheet,result):
    column = 0
    row = 0
    for i in xrange(len(result)):
        row = row + 1
        for value in result[i].values():
            sheet.write(row,column,value)
            column = column + 1
        column = 0

wbk = xlwt.Workbook()
sheet = wbk.add_sheet('Sheet4',cell_overwrite_ok=True)
today = datetime.today()
result = [{'id':1,'name':'zhangsan'},{'id':2,'name':'zhangsi'}]
write_sheet_title(sheet,result[0])
write_sheet_data(sheet,result)
wbk.save('test.xls')
