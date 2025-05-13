
# /// script
# dependencies = [
#     "marimo",
#     "plotly==6.0.1",
#     "polars==1.29.0",
#     "requests==2.32.3",
#     "numpy==2.2.5",
# ]
# [tool.marimo.display]
# theme = "dark"
# [tool.marimo.runtime]
# watcher_on_save = "autorun"
# ///

import marimo

__generated_with = "0.13.2"
app = marimo.App(width="full")

with app.setup:
    from io import StringIO
    import requests

    import marimo as mo
    import plotly.express as px
    import polars as pl




@app.cell
def _(drop, drop_units):
    units = 'metric' if drop_units.value == 'C' else 'standard'
    start_date = f'{drop.value}-01-01T00:00:00-07:00'
    end_date = '2025-05-14T00:00:00-07:00'
    url = f'https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations=USW00023183&startDate={start_date}&endDate={end_date}&dataTypes=TMAX,TMIN,TAVG&format=csv&units={units}'
    headers = {
        'User-Agent': 'phx weekend temps notebook'
    }
    response = requests.get(url, headers=headers)

    return (response,)


@app.cell
def _(response):
    lf = (
        pl.scan_csv(StringIO(response.text))
        .select(
            pl.col('DATE').str.to_date('%Y-%m-%d'),
            pl.when(pl.col('DATE').str.to_date('%Y-%m-%d').dt.weekday().is_in([1,2,3,4,5]))
                .then(pl.lit('weekday'))
                .otherwise(pl.lit('weekend')).alias('weekday'),
            pl.col('TMAX').alias(f'max_temp_{drop_units.value}')
        )
        .sort('DATE')
        .group_by_dynamic('DATE', every='1mo', group_by='weekday')
        .agg(pl.col(f'max_temp_{drop_units.value}').mean().alias(f'avg_max_temp_{drop_units.value}'))
    )
    df = lf.collect()
    df
    return (df,)

@app.cell
def _():
    drop = mo.ui.dropdown(range(2000,2025), value=2022)
    drop_units = mo.ui.dropdown(['F', 'C'], value='F')
    mo.md(f"""
    select a start year:  
          {drop}
    F or C?
          {drop_units}
    """)
    return (drop, drop_units)

@app.cell
def _(df):
    fig = px.line(df, x='DATE', y=f'avg_max_temp_{drop_units.value}', color='weekday', title='weekend weather')
    fig.update_xaxes(
        tickformat='%b\n%Y'
    )
    fig
    return


if __name__ == "__main__":
    app.run()
