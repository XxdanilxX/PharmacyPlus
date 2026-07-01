from datetime import datetime

from bson import ObjectId
from flask import Blueprint, redirect, render_template, request
from pymongo import DESCENDING

from .. import db as database
from ..constants import PHARMACIES

bp = Blueprint("sales", __name__, url_prefix="/sales")


@bp.route("/")
def list_sales():
    page = int(request.args.get("page", 1))
    limit = 15
    skip = (page - 1) * limit

    total = database.sales_col.count_documents({})
    pages = max(1, (total + limit - 1) // limit)
    sales = list(
        database.sales_col.find().sort("date", DESCENDING).skip(skip).limit(limit)
    )

    summary = list(
        database.sales_col.aggregate(
            [{"$group": {"_id": None, "total": {"$sum": "$total"}, "cnt": {"$sum": 1}}}]
        )
    )
    total_revenue = summary[0]["total"] if summary else 0
    count = summary[0]["cnt"] if summary else 0
    average_bill = total_revenue / count if count else 0

    return render_template(
        "sales/list.html",
        active="sales",
        sales=sales,
        page=page,
        pages=pages,
        count=count,
        total_revenue=total_revenue,
        average_bill=average_bill,
    )


@bp.route("/add", methods=["GET", "POST"])
def add_sale():
    medications = list(database.meds_col.find().sort("name", 1))
    error = None

    if request.method == "POST":
        medication_id = request.form["medication_id"]
        quantity = int(request.form.get("quantity", 1))
        medication = (
            database.meds_col.find_one({"_id": ObjectId(medication_id)})
            if ObjectId.is_valid(medication_id)
            else None
        )

        if medication and quantity > 0:
            if quantity > medication["quantity"]:
                error = (
                    "Недостатньо товару на складі. "
                    f"Доступно: {medication['quantity']} {medication['unit']}"
                )
            else:
                database.sales_col.insert_one(
                    {
                        "medication_id": medication_id,
                        "medication_name": medication["name"],
                        "quantity": quantity,
                        "price": medication["price"],
                        "total": round(medication["price"] * quantity, 2),
                        "date": datetime.now(),
                        "pharmacy": request.form.get("pharmacy", PHARMACIES[0]),
                    }
                )
                database.meds_col.update_one(
                    {"_id": ObjectId(medication_id)}, {"$inc": {"quantity": -quantity}}
                )
                return redirect("/sales/")

    return render_template(
        "sales/add.html",
        active="add",
        medications=medications,
        pharmacies=PHARMACIES,
        error=error,
    )
