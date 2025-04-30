# /// script
# dependencies = [
#     "marimo",
#     "watchdog",
# ]
# [tool.marimo.runtime]
# watcher_on_save = 'autorun'
# ///

import marimo

__generated_with = "0.13.2"
app = marimo.App(width="compact", css_file='public/ayu.css')

with app.setup:
    import marimo as mo
    import csv


@app.cell
def _():
    mo.md('# MME Calculator')
    return

@app.cell
def _():
    with open('public/conversion_factors.csv', 'r') as cf:
        reader = csv.reader(cf)
        conversion_factors = {row[0]: float(row[1]) for row in reader}

    opi_drop = mo.ui.dropdown(options=conversion_factors.keys(), value='Codeine', label='Drug')
    strength = mo.ui.number(start=0, value=50, label='Strength/Unit')
    quantity = mo.ui.number(start=0, value=30, label='Quantity')
    days_supply = mo.ui.number(start=0, value=30, label='Days Supply')
    row_1 = mo.hstack([opi_drop, strength], align='center')
    row_2 = mo.hstack([quantity, days_supply], align='center')
    mme_inputs = mo.vstack([row_1, row_2], align='start')

    mo.md(f"""
    ### Inputs:  
    {mme_inputs}
    """)
    return conversion_factors, days_supply, opi_drop, quantity, strength


@app.cell
def _(mme):
    if mme >= 90:
        call_kind = 'alert'
    else:
        call_kind = 'info'
    mo.callout(f'Calculated daily MME value: {mme}', kind=call_kind)
    return

@app.cell
def _(conversion_factors, days_supply, opi_drop, quantity, strength):
    drug_cf = conversion_factors[opi_drop.value]
    mme = round(float(strength.value) * (float(quantity.value) / float(days_supply.value)) * drug_cf, 2)
    mo.md(f"""
    ### MME Calculation
    *MME = strength * (quantity / days_supply) * conversion factor*[^1]  

    `{opi_drop.value}` conversion factor: `{drug_cf}`
    #### **{mme}** = {strength.value} * ({quantity.value} / {days_supply.value}) * {drug_cf}  

    [^1]: [Conversion Factors from CDC Prescribing Guidelines](https://www.cdc.gov/mmwr/volumes/71/rr/rr7103a1.htm#T1_down)
    """)
    return (mme,)


if __name__ == "__main__":
    app.run()
