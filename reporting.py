import uuid
import logging
import io
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
from datetime import datetime
from PIL import ImageFont, Image, ImageDraw

logging.basicConfig(
    format='%(asctime)-24s %(filename)-20s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger()


def getyearmonth(row):
    return datetime.utcfromtimestamp(row['delivery_time.$date']/1000).strftime('%Y-%m')

def parseOrdersFromRequest(content):
    inputs = [ pd.json_normalize(json.loads(x)) for x in content.values() if x ]
    orders = pd.concat(inputs)
    orders = orders.drop_duplicates(subset="order_id")
    return orders

def parseOrdersFromFile():
    f = open('anita.json', 'r')
    data = json.load(f)
    return pd.json_normalize(data)

def generateReport(orders):
        
    orders['venue_name_fixed'] = orders['venue_name'].str.extract(
        r'([^\\/|+]*)')
    orders = orders[orders['status'] == 'delivered']
    orders["year-month"] = orders.apply(lambda row: getyearmonth(row), axis=1)
    orders = orders[orders['year-month'].str.startswith('2021')]

    best_rest = orders.groupby('venue_name_fixed').sum('total_price')
    best_rest = best_rest.sort_values(
        'total_price', ascending=False).total_price/100

    monthly = orders.groupby('year-month').sum('total_price').total_price/100

    items = orders.explode('items')
    items = items[items['items'].notna()]
    items["item_name"] = items['items'].map(lambda x: x["name"])
    items["item_count"] = items['items'].map(lambda x: x["count"])
    items["item_total_price"] = items['items'].map(lambda x: x["end_amount"])

    best_items = items.groupby('item_name').sum('item_total_price')
    best_items = best_items.sort_values(
        'item_total_price', ascending=False).item_total_price/100

    imageUUID = uuid.uuid4().hex
    FIG_FILENAME = f'wolt/reports/{imageUUID}.png'

    QLEN = 600

    pio.kaleido.scope.default_format = "svg"
    pio.kaleido.scope.default_width = QLEN
    pio.kaleido.scope.default_height = QLEN

    myImage = Image.new(mode="RGB", size=(
        1200, 1200), color=(255, 255, 255, 0))

    numFont = ImageFont.truetype("public/static/Ubuntu.ttf", 40)
    headFont = ImageFont.truetype("public/static/Ubuntu.ttf", 40, )

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
    str = f"{orders['total_price'].sum()/100:,}"
    draw = ImageDraw.Draw(myImage)
    length = draw.textsize(str, font=numFont)[0]
    draw.text(((QLEN-length)/2, 300), str, font=numFont, fill="black")

    str = f"Average Order"
    draw = ImageDraw.Draw(myImage)
    length = draw.textsize(str, font=headFont)[0]
    draw.text(((QLEN-length)/2, 420), str, font=headFont, fill="black")
    #str = (orders['total_price'].mean()/100).astype('str')
    str = f"{orders['total_price'].mean()/100:,.2f}"
    draw = ImageDraw.Draw(myImage)
    length = draw.textsize(str, font=numFont)[0]
    draw.text(((QLEN-length)/2, 480), str, font=numFont, fill="black")

    chart = px.bar(monthly, title="Monthly Expenses", text_auto=True, labels={
                   "value": "Total Expense", "year-month": "Month"})
    chart.update_layout(showlegend=False)
    chart_bytes = chart.to_image(format="png")
    img = Image.open(io.BytesIO(chart_bytes))
    myImage.paste(img, (QLEN, 0))

    chart = px.bar(best_rest[0:10], title="Top 10 Restaurants", color='value', text_auto=True, labels={
                   "value": "Total Expense", "venue_name_fixed": "Restaurant Name"})
    chart.update_xaxes(tickangle=30)
    chart.update_layout(showlegend=False)
    chart_bytes = chart.to_image(format="png")
    img = Image.open(io.BytesIO(chart_bytes))
    myImage.paste(img, (0, QLEN))

    chart = px.bar(best_items[0:10], title="Top 10 dishes", color='value', text_auto=True, labels={
        "value": "Total Expense", "item_name": "Dish"})
    chart.update_layout(showlegend=False)
    chart_bytes = chart.to_image(format="png")
    img = Image.open(io.BytesIO(chart_bytes))
    myImage.paste(img, (QLEN, QLEN))

    myImage.save(FIG_FILENAME)

    return imageUUID


def main():

    df = parseOrdersFromFile()
    generateReport(df)


if __name__ == "__main__":
    main()
