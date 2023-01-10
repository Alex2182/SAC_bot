import pandas as pd
import psycopg2 as pg
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from tabulate import tabulate

month={
       '01':'январь',
       '02':'февраль',
       '03':'март',
       '04':'апрель',
       '05':'май',
       '06':'июнь',
       '07':'июль',
       '08':'август',
       '09':'сентябрь',
       '10':'октябрь',
       '11':'ноябрь',
       '12':'декабрь'
       }


def pic_pf():
   msg="Выполнение плана на дату"
   engine = pg.connect(dbname='abonin', user='ksc', password='KSC.local', host='10.121.2.29')
   df1 = pd.read_sql("select MAX(Дата) as cur_date from testplanfact", con=engine)
   df = pd.read_sql('select Подразделение as x, AVG("Месяц Номенклатура % выполнения")  as value from testplanfact where Дата=(select MAX(Дата) from testplanfact) group by Подразделение order by Подразделение', con=engine)
   s=df1['cur_date']
   date=s[0].strftime("%d.%m.%Y")
   # Plotly example
   fig = go.Figure(data=[
       go.Bar(name='План по номенклатуре', y=df['x'], x=df['value'], orientation='h',text=df['value'],texttemplate='%{x:.2f}%'),
   ])
   
   fig.update_layout(width=2048, height=1400, title=f"Выполнение плана на дату {date}",)
   fig.write_image("lastplanfact.png")
   engine.close()

def effect(shop):
    if(shop.find('Итого')>-1):
       label = 'в целом по КСК МК'
    else:
       label = f'для {shop} цеха'
    engine = pg.connect(dbname='abonin', user='ksc', password='KSC.local', host='10.121.2.29')
    df1 = pd.read_sql(f"SELECT ПЛАН_ФАКТ_КОРР*100 as value,ДАТА as date FROM KPI_production WHERE KPI_production.ПОДРАЗДЕЛЕНИЕ='{shop}' AND ТИП='Натуральное выражение' ORDER BY ДАТА", con=engine)
    df2 = pd.read_sql(f"SELECT ПЛАН_ФАКТ_КОРР*100 as value,ДАТА as date FROM KPI_production WHERE KPI_production.ПОДРАЗДЕЛЕНИЕ='{shop}' AND ТИП='Денежное выражение' ORDER BY ДАТА", con=engine)
    df3 = pd.read_sql(f"SELECT ПЛАН_ФАКТ_КОРР*100 as value,ДАТА as date FROM KPI_production WHERE KPI_production.ПОДРАЗДЕЛЕНИЕ='{shop}' AND ТИП='Выработка' ORDER BY ДАТА", con=engine)
    fig = go.Figure(data=[
        go.Bar(name='Натуральное выражение', x=df1['date'], y=df1['value'],text=df1['value'], texttemplate='%{y:.2f}%'),
        go.Bar(name='Денежное выражение', x=df2['date'], y=df2['value'],text=df2['value'], texttemplate='%{y:.2f}%'),
        go.Bar(name='Выработка', x=df3['date'], y=df3['value'],text=df3['value'], texttemplate='%{y:.2f}%')
    ])
    # Change the bar mode
    fig.update_layout(barmode='group',width=2048, height=1400, title=f'Выполнение плана по месяцам {label}',legend=dict(
        orientation="h",
        yanchor="bottom",
        xanchor="right",
        x=1,
        y=1,
    ))
    # fig.update_layout(width=800, height=600, title=f"Выполнение по месяцам {shop} цеха",)
    fig.write_image("effect.png")
    engine.close()


def otk():
    engine = pg.connect(dbname='abonin', user='ksc', password='KSC.local', host='10.121.2.29')
    df1 = pd.read_sql("SELECT MAX(Дата) AS cur_date, to_char(MAX(Дата),'mm') as cur_month_name FROM kpi_otk", con=engine)
    df = pd.read_sql("SELECT Цех AS x,SUM(Значение) AS y FROM kpi_otk WHERE Показатель='1.2.N.забр.' OR Показатель='1.1.N.испр.' AND Дата=(select MAX(Дата) as cur_date FROM kpi_otk) GROUP BY Цех", con=engine)
    #df = pd.read_sql("SELECT Цех AS x,Значение AS y FROM kpi_otk WHERE Показатель='1.2.N.забр.' OR Показатель='1.1.N.испр.' AND Дата=(select MAX(Дата) as cur_date FROM kpi_otk)", con=engine)
    s=df1['cur_month_name']
    date=month.get(s[0])
    # Plotly example
    fig = go.Figure(data=[
        go.Bar(name='Количество несоответствующей продукции', x=df['x'], y=df['y'], orientation='v', text=df['y'], textposition='auto'),
    ])
    # Change the bar mode
    fig.update_layout(width=2048, height=1400, title=f"Количество несоответствующей продукции {date}, шт.",)
    fig.write_image("otk.png")
    engine.close()

def devicewrk(shop):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # shop='256'
    engine = pg.connect(dbname='abonin', user='ksc', password='KSC.local', host='10.121.2.29')
    df1 = pd.read_sql(f"SELECT Дата AS x, SUM(Тработы)/SUM(Тфонд) AS y, SUM(Твкл)/SUM(Тфонд) AS y2  FROM device_work WHERE Цех='{shop}' AND Твкл>0 GROUP BY Дата ORDER BY Дата", con=engine)
    # Add traces
    fig.add_trace(go.Scatter(x=df1['x'], y=df1['y2']*100, name="Коэф доступности"),secondary_y=False,)
    fig.add_trace(go.Scatter(x=df1['x'], y=df1['y']*100, name="Коэф работы"),secondary_y=False,)
    # Add figure title
    fig.update_layout(title_text=f"Загрузка оборудования за всё время по цеху {shop}",legend=dict(
     orientation="h", yanchor="bottom", xanchor="right", x=1, y=1,))
    # Set x-axis title
    fig.update_xaxes(title_text="Месяца")

    # Set y-axes titles
    fig.update_yaxes(title_text="Коэф доступности", secondary_y=False)
    fig.update_yaxes(title_text="%", secondary_y=False)
    fig.write_image("devicewrk.png")
    engine.close()
def find_artikul(artikul):
    now = datetime.now() # current date and time
    # artikul='04.01.00.01.004'
    year = now.strftime("%Y")
    month = int(now.strftime("%m"))+1
    engine = pg.connect(dbname='abonin', user='ksc', password='KSC.local', host='10.121.2.29')
    df = pd.read_sql(f"SELECT artikul,har,tm_pol,SUM(kol) as summa from pd WHERE period<'{year}-{month}-1' AND artikul='{artikul}' GROUP BY artikul,har,tm_pol", con=engine)
    fig = go.Figure(
    data=
    [
    go.Table(columnwidth = [120,120,80,80],
    header=dict(values=['<b>Артикул</b>','<b>Характеристика</b>','<b>Получатель</b>','<b>Количество</b>']),
    cells=dict(values=[df.artikul, df.har, df.tm_pol, df.summa]))
    ]
    )
    fig.update_layout(width=2048, height=1400)
    fig.write_image("tvz.png")

def artikul_history(artikul):
    now = datetime.now() # current date and time
#    artikul='010001104500'
    year = now.strftime("%Y")
# print("year:", year)
    month = int(now.strftime("%m"))+1
# print("month:", int(month)+1)
    engine = pg.connect(dbname='abonin', user='ksc', password='KSC.local', host='10.121.2.29')
    df = pd.read_sql(f"SELECT artikul,har as Характеристика,tm_pol,SUM(kol) as summa, substring(file_id,3,6) as file from pd WHERE period<'{year}-{month}-1' AND artikul='{artikul}' GROUP BY artikul,Характеристика,file,tm_pol ORDER BY Характеристика asc", con=engine)
    table = pd.pivot_table(df, values='summa', index='Характеристика', columns=['file'],margins=True,margins_name='Итого',sort=False)
# table.reset_index()
    text = tabulate(table, headers='keys', tablefmt='fancy_grid',showindex=True)
    text = text.replace('\n','\r\n')
    return f'Артикул {artikul}\n{text}'

# print(artikul_history('010001104500'))
