from collections import defaultdict
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request

from .. import db as database

bp = Blueprint("forecast", __name__, url_prefix="/forecast")


@bp.route("/")
def forecast():
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    medications = list(database.meds_col.find())
    results = []

    for medication in medications:
        medication_id = str(medication["_id"])
        daily = defaultdict(int)

        for sale in database.sales_col.find({"medication_id": medication_id}):
            daily[sale["date"].strftime("%Y-%m-%d")] += sale["quantity"]

        if not daily:
            continue

        series = [
            daily.get((today - timedelta(days=i)).strftime("%Y-%m-%d"), 0)
            for i in range(14, 0, -1)
        ]
        count = len(series)
        average_daily = sum(series) / count

        midpoint = (count - 1) / 2
        numerator = sum(
            (i - midpoint) * (series[i] - average_daily) for i in range(count)
        )
        denominator = sum((i - midpoint) ** 2 for i in range(count)) or 1
        slope = numerator / denominator

        forecast_7 = [max(0, round(average_daily + slope * i, 1)) for i in range(1, 8)]
        forecast_sum = sum(forecast_7)
        days_to_stockout = int(medication["quantity"] / average_daily) if average_daily > 0 else 999

        results.append(
            {
                "id": medication_id,
                "name": medication["name"],
                "category": medication["category"],
                "quantity": medication["quantity"],
                "unit": medication["unit"],
                "avg_daily": round(average_daily, 1),
                "slope": round(slope, 2),
                "forecast_7": forecast_7,
                "forecast_sum": round(forecast_sum, 1),
                "days_to_stock": days_to_stockout,
                "will_out": forecast_sum > medication["quantity"],
            }
        )

    results.sort(key=lambda item: item["days_to_stock"])

    selected_name = request.args.get("med", results[0]["name"] if results else "")
    selected = next(
        (item for item in results if item["name"] == selected_name),
        results[0] if results else None,
    )

    labels = []
    history_values = []
    forecast_values = []

    if selected:
        selected_daily = defaultdict(int)
        for sale in database.sales_col.find({"medication_id": selected["id"]}):
            selected_daily[sale["date"].strftime("%Y-%m-%d")] += sale["quantity"]

        for i in range(14, 0, -1):
            day = today - timedelta(days=i)
            labels.append(day.strftime("%d.%m"))
            history_values.append(selected_daily.get(day.strftime("%Y-%m-%d"), 0))
            forecast_values.append(None)

        for i, value in enumerate(selected["forecast_7"], 1):
            labels.append((today + timedelta(days=i)).strftime("%d.%m"))
            history_values.append(None)
            forecast_values.append(value)

    return render_template(
        "forecast.html",
        active="forecast",
        results=results,
        selected_name=selected_name,
        labels=labels,
        history_values=history_values,
        forecast_values=forecast_values,
    )
