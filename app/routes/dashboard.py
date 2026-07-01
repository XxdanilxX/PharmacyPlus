from collections import defaultdict
from datetime import datetime, timedelta
import random

from bson import ObjectId
from flask import Blueprint, redirect, render_template, request
from pymongo import DESCENDING

from .. import db as database
from ..constants import PHARMACIES

bp = Blueprint("dashboard", __name__)


@bp.route("/seed")
def seed():
    database.meds_col.drop()
    database.sales_col.drop()

    med_list = [
        ("Амоксицилін 500 мг", "Антибіотики", 45.00, 120, 20, "таб."),
        ("Ібупрофен 400 мг", "Знеболюючі", 28.50, 200, 30, "таб."),
        ("Вітамін C 1000 мг", "Вітаміни", 35.00, 180, 25, "таб."),
        ("Лоратадин 10 мг", "Антигістамінні", 22.00, 90, 15, "таб."),
        ("Аспірин 500 мг", "Знеболюючі", 18.00, 14, 20, "таб."),
        ("Корвалол 25 мл", "Серцево-судинні", 55.00, 60, 10, "флак."),
        ("Осельтамівір 75 мг", "Противірусні", 280.00, 7, 15, "капс."),
        ("Еналаприл 10 мг", "Серцево-судинні", 65.00, 45, 10, "таб."),
        ("Мультівітаміни", "Вітаміни", 120.00, 70, 10, "таб."),
        ("Парацетамол 500 мг", "Знеболюючі", 12.00, 300, 50, "таб."),
        ("Цетиризин 10 мг", "Антигістамінні", 19.00, 55, 10, "таб."),
        ("Магне B6", "Вітаміни", 95.00, 40, 10, "таб."),
    ]

    manufacturers = [
        "Фармак",
        "Дарниця",
        "Борщагівський ХФЗ",
        "Здоров'я",
        "Київмедпрепарат",
    ]

    med_ids = []
    for name, category, price, quantity, min_quantity, unit in med_list:
        inserted_id = database.meds_col.insert_one(
            {
                "name": name,
                "category": category,
                "price": price,
                "quantity": quantity,
                "min_quantity": min_quantity,
                "unit": unit,
                "manufacturer": random.choice(manufacturers),
                "created_at": datetime.now(),
            }
        ).inserted_id
        med_ids.append((str(inserted_id), name, price))

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    for day_offset in range(30, 0, -1):
        sale_date = today - timedelta(days=day_offset)
        for _ in range(random.randint(3, 8)):
            med_id, name, price = random.choice(med_ids)
            quantity = random.randint(1, 5)
            database.sales_col.insert_one(
                {
                    "medication_id": med_id,
                    "medication_name": name,
                    "quantity": quantity,
                    "price": price,
                    "total": round(price * quantity, 2),
                    "date": sale_date + timedelta(hours=random.randint(8, 20)),
                    "pharmacy": random.choice(PHARMACIES),
                }
            )

    return redirect("/?seeded=1")


@bp.route("/")
def index():
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    total_meds = database.meds_col.count_documents({})
    low_stock = list(
        database.meds_col.find({"$expr": {"$lte": ["$quantity", "$min_quantity"]}})
    )
    today_sales = list(database.sales_col.find({"date": {"$gte": today}}))
    today_revenue = sum(sale["total"] for sale in today_sales)
    total_stock_value = sum(
        med["price"] * med["quantity"] for med in database.meds_col.find()
    )
    recent_sales = list(database.sales_col.find().sort("date", DESCENDING).limit(8))

    week_sales = list(
        database.sales_col.find({"date": {"$gte": today - timedelta(days=7)}})
    )
    category_revenue = defaultdict(float)
    for sale in week_sales:
        medication_id = sale.get("medication_id")
        medication = (
            database.meds_col.find_one({"_id": ObjectId(medication_id)})
            if ObjectId.is_valid(medication_id)
            else None
        )
        if medication:
            category_revenue[medication["category"]] += sale["total"]

    return render_template(
        "dashboard.html",
        active="home",
        seeded=request.args.get("seeded"),
        total_meds=total_meds,
        low_stock=low_stock,
        today_revenue=today_revenue,
        total_stock_value=total_stock_value,
        recent_sales=recent_sales,
        category_labels=list(category_revenue.keys()),
        category_values=[round(value, 2) for value in category_revenue.values()],
    )
