import model
from FieldType import *
import datetime

class stock(model.model):
    stock_date = FieldType(datetime.date, 1)
    stock_code = FieldType(str, 2)
    stock_name = FieldType(str, 3)
    stock_close_price = FieldType(float, 4)
    stock_max_price = FieldType(float, 5)
    stock_min_price = FieldType(float, 6)
    stock_open_price = FieldType(float, 7)
    stock_yesterday_close_price = FieldType(float, 8)
    stock_rise_and_fall_amount = FieldType(float, 9)
    stock_rise_and_fall_rate = FieldType(float, 10)
    stock_turnover_rate = FieldType(float, 11)
    stock_volumes = FieldType(float, 12)
    stock_volumes_amount = FieldType(float, 13)
    stock_all_market_cap = FieldType(float, 14)
    stock_circulate_market_cap = FieldType(float, 15)

    class Meta:
        file = 'E:\\1.xlsx'

if __name__ == "__main__":
    m_obj = stock()
    rowOffset = 2
    while True:
        ret = m_obj.readLine(rowOffset)
        if not ret:
            break
        for (k,v) in ret.__dict__.items():
            if k.startswith('stock_'):
                print(v)
        print('-----------------------\r')
        rowOffset += 1
