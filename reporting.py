import uuid
import logging
import io
import json
import pytz
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
from datetime import datetime
from time import mktime
from PIL import ImageFont, Image, ImageDraw
from dateutil.relativedelta import relativedelta


logging.basicConfig(
    format='%(asctime)-24s %(filename)-20s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger()


def getyearmonth(row):
    return datetime.utcfromtimestamp(row['delivery_time.$date']/1000).strftime('%Y-%m')


def parseOrdersFromRequest(content):
    inputs = [pd.json_normalize(json.loads(x)) for x in content.values() if x]
    orders = pd.concat(inputs)
    orders = orders.drop_duplicates(subset="order_id")
    return orders


def parseOrdersFromFile():
    f = open('temp/test.json', 'r')
    data = json.load(f)
    return pd.json_normalize(data)


def generateReport(orders, filename=None):

    orders['venue_name_fixed'] = orders['venue_name'].str.extract(
        r'([^\\/|+]*)')
    orders = orders[orders['status'] == 'delivered']
    orders["year-month"] = orders.apply(lambda row: getyearmonth(row), axis=1)
    orders['myitems'] = orders.apply(lambda row: row["items"] if row["items"]==row["items"] else row["group.my_member.items"], axis=1)
    orders['myprice'] = orders.apply(lambda row: row["total_price_share"] if row["total_price_share"] > 0 else row["total_price"], axis=1)

    lastYear = mktime((datetime.today().date().replace(day=1) - relativedelta(years=1)).timetuple()) * 1000
    orders = orders[orders['delivery_time.$date'] >= lastYear]

    monthly = (orders.groupby(['currency', 'year-month']).sum(
        'myprice').sort_values(['myprice']).myprice/100).reset_index(level=['currency', 'year-month'])

    items = orders.explode('myitems')
    items["item_name"] = items['myitems'].map(lambda x: x["name"])
    items["item_count"] = items['myitems'].map(lambda x: x["count"])
    items["item_total_price"] = items['myitems'].map(lambda x: x["end_amount"])
    
    totals = (orders[['currency','myprice']].groupby(['currency']).sum().sort_values('myprice', ascending=False)/100).to_dict()['myprice']
    averages = (orders[['currency','myprice']].groupby(['currency']).mean().sort_values('myprice', ascending=False)/100).to_dict()['myprice']

    orders_heatmap = pd.DataFrame(np.zeros((5, 7)))

    for index, row in orders.iterrows():

        timezone = pytz.timezone(row["venue_timezone"])
        timestamp = datetime.fromtimestamp(
            row['delivery_time.$date']/1000, timezone)

        weekday = int(timestamp.strftime('%w'))
        hour = int(timestamp.strftime('%H'))

        if hour <= 6:
            timeofday = 4
        elif hour <= 12:
            timeofday = 0
        elif hour <= 16:
            timeofday = 1
        elif hour <= 19:
            timeofday = 2
        elif hour <= 24:
            timeofday = 3
        else:
            timeofday = 4

        orders_heatmap[weekday][timeofday] += 1

    everything = items.groupby(['currency', 'venue_name_fixed', 'item_name']).agg(
        {"item_total_price": lambda x: np.sum(x)/100}).reset_index()

    imageUUID = uuid.uuid4().hex
    FIG_FILENAME = f'wolt/reports/{imageUUID}.jpg'

    QLEN = 600

    pio.kaleido.scope.default_format = "svg"
    pio.kaleido.scope.default_width = QLEN
    pio.kaleido.scope.default_height = QLEN

    myImage = Image.new(mode="RGB", size=(
        QLEN*3, QLEN*2), color=(255, 255, 255, 0))

    headFont = ImageFont.truetype("public/static/Ubuntu.ttf", 40)
    numFont = ImageFont.truetype("public/static/Ubuntu.ttf", 30)

    str = f"Order Count"
    draw = ImageDraw.Draw(myImage)
    length = draw.textsize(str, font=headFont)[0]
    draw.text(((QLEN-length)/2, 60), str, font=headFont, fill="black")
    str = f"{orders['order_id'].count()}"
    draw = ImageDraw.Draw(myImage)
    length = draw.textsize(str, font=numFont)[0]
    draw.text(((QLEN-length)/2, 120), str, font=numFont, fill="black")

    str = f"Total Expenses"
    draw = ImageDraw.Draw(myImage)
    length = draw.textsize(str, font=headFont)[0]
    draw.text(((QLEN-length)/2, 240), str, font=headFont, fill="black")
    str = " / ".join(f'{tup[1]:.1f} {tup[0]}'  for tup in list(totals.items()))
    draw = ImageDraw.Draw(myImage)
    length = draw.textsize(str, font=numFont)[0]
    draw.text(((QLEN-length)/2, 300), str, font=numFont, fill="black")

    str = f"Average Order"
    draw = ImageDraw.Draw(myImage)
    length = draw.textsize(str, font=headFont)[0]
    draw.text(((QLEN-length)/2, 420), str, font=headFont, fill="black")
    str = " / ".join(f'{tup[1]:.1f} {tup[0]}'  for tup in list(averages.items()))
    draw = ImageDraw.Draw(myImage)
    length = draw.textsize(str, font=numFont)[0]
    draw.text(((QLEN-length)/2, 480), str, font=numFont, fill="black")

    chart = px.bar(monthly, title="Monthly Expenses", text_auto=True, barmode='group', color='currency', x='year-month', y='myprice',
                   labels={"myprice": "Total Expense", "year-month": "Month"})
    chart.update_xaxes(tickangle=30, showticklabels=True)

    chart_bytes = chart.to_image(format="jpg")
    img = Image.open(io.BytesIO(chart_bytes))
    myImage.paste(img, (QLEN, 0))

    labels_x = ['Sun', 'Mon', 'Tue',
                'Wed', 'Thu', 'Fri', 'Sat']
    labels_y = ['Morning (6-12)', 'Noon (12-16)',
                'Afternoon (16-19)', 'Evening (19-22)', 'Night (22-6)']

    chart = px.imshow(orders_heatmap, title='Delivery Time Distribution', y=labels_y, x=labels_x,
                      aspect='auto', text_auto=True)
    chart.update_layout(coloraxis_showscale=False)
    chart.update_xaxes(side="top")
    chart_bytes = chart.to_image(format="jpg")
    img = Image.open(io.BytesIO(chart_bytes))
    myImage.paste(img, (QLEN*2, 0))

    chart = px.treemap(everything, path=['currency', 'venue_name_fixed', 'item_name'], values=('item_total_price'), color_continuous_scale='RdBu',
                       height=QLEN, width=QLEN*3)
    chart.update_traces(texttemplate='%{label}:%{value}')
    chart.update_layout(margin=dict(t=0, l=0, r=0, b=0))
    chart_bytes = chart.to_image(format="jpg")
    img = Image.open(io.BytesIO(chart_bytes))
    myImage.paste(img, (0, QLEN))

    myImage.save(filename or FIG_FILENAME)

    return imageUUID


def main():

    df = parseOrdersFromFile()
    generateReport(df, 'temp/output.png')


if __name__ == "__main__":
    main()
