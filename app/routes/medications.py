from datetime import datetime

from bson import ObjectId
from flask import Blueprint, redirect, render_template, request

from .. import db as database
from ..constants import CATEGORIES, UNITS

bp = Blueprint("medications", __name__, url_prefix="/medications")


@bp.route("/")
def list_medications():
    search = request.args.get("q", "").strip()
    category = request.args.get("cat", "")

    query = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if category:
        query["category"] = category

    medications = list(database.meds_col.find(query).sort("name", 1))
    categories = sorted(database.meds_col.distinct("category"))

    return render_template(
        "medications/list.html",
        active="med",
        medications=medications,
        categories=categories,
        selected_category=category,
        search=search,
    )


@bp.route("/add", methods=["GET", "POST"])
def add_medication():
    if request.method == "POST":
        database.meds_col.insert_one(_form_data())
        return redirect("/medications/")

    return render_template(
        "medications/form.html",
        active="med",
        title="Додати медикамент",
        medication={},
        categories=CATEGORIES,
        units=UNITS,
    )


@bp.route("/edit/<medication_id>", methods=["GET", "POST"])
def edit_medication(medication_id):
    if not ObjectId.is_valid(medication_id):
        return redirect("/medications/")

    medication = database.meds_col.find_one({"_id": ObjectId(medication_id)})
    if not medication:
        return redirect("/medications/")

    if request.method == "POST":
        database.meds_col.update_one(
            {"_id": ObjectId(medication_id)},
            {"$set": _form_data(include_created_at=False)},
        )
        return redirect("/medications/")

    return render_template(
        "medications/form.html",
        active="med",
        title=f"Редагувати: {medication['name']}",
        medication=medication,
        categories=CATEGORIES,
        units=UNITS,
    )


@bp.route("/delete/<medication_id>")
def delete_medication(medication_id):
    if ObjectId.is_valid(medication_id):
        database.meds_col.delete_one({"_id": ObjectId(medication_id)})
    return redirect("/medications/")


def _form_data(include_created_at=True):
    data = {
        "name": request.form["name"].strip(),
        "category": request.form["category"],
        "price": float(request.form["price"]),
        "quantity": int(request.form["quantity"]),
        "min_quantity": int(request.form["min_quantity"]),
        "unit": request.form["unit"],
        "manufacturer": request.form.get("manufacturer", "").strip(),
    }
    if include_created_at:
        data["created_at"] = datetime.now()
    return data
