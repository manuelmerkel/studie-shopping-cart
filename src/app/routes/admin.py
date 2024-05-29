from flask import Blueprint, session, redirect, url_for, render_template, flash, g

from src.app.controllers import OrderController
from src.app.routes.user import login_required
from collections import defaultdict

admin_area_blueprint = Blueprint("admin_area", __name__, url_prefix="/admin")
admin_product_info_blueprint = Blueprint(
    "admin_product_info", __name__, url_prefix="/admin/products"
)
admin_orders_info_blueprint = Blueprint(
    "admin_orders_info", __name__, url_prefix="/admin/orders"
)


@admin_area_blueprint.route("/")
@login_required
def admin_area():
    first_name = session["first_name"]
    if "admin" not in first_name:
        flash("You are not an admin", "warning")
        return redirect(url_for("root.root"))
    return render_template(
        "adminArea.html",
        firstName=first_name,
        noOfItems=session["no_of_items"],
        loggedIn=session["logged_in"],
    )


@admin_product_info_blueprint.route("/")
@login_required
def admin_available_products_statistics():
    return redirect(url_for("root.root"))


@admin_orders_info_blueprint.route("/")
def admin_orders_statistics():
    ses = g.session
    orders = OrderController(ses).get_orders_with_product_info()

    dynamic_data_table = get_dynamic_table(orders)

    return render_template(
        "adminOrderStats.html",
        cloumnHeaders=dynamic_data_table[0],
        tableValues=dynamic_data_table[1:],
        firstName=session["first_name"],
        noOfItems=session["no_of_items"],
        loggedIn=session["logged_in"],
    )


def get_dynamic_table(orders: list[list[str | int]]) -> list[list[str | int]]:
    """
    orders besteht aus einer Liste aus Listen. Eine Liste besteht jeweils aus einer order_item_id (int), einer order_id (int) und
    dem product_name (str).

    :param orders: list[list[str | int]]
    :return: das 2d Array mit der Statistik mit den product_name als Spaltennamen und der order_id als Reihennamen
    """

    if not orders:
        return []

    from collections import defaultdict

    # Dictionary zur Speicherung der Anzahl der Produkte pro Bestellung
    order_totals = defaultdict(lambda: defaultdict(int))
    product_names = set()

    # Sammle die Produktnamen und fülle das Dictionary
    for _, order_id, product_name in orders:
        order_totals[order_id][product_name] += 1
        product_names.add(product_name)

    # Sortiere die Produktnamen alphabetisch
    sorted_product_names = sorted(product_names)

    # Erstelle die Header-Zeile
    header = ["Order ID"] + sorted_product_names + ["Total"]

    # Erstelle die Tabelle und berechne die Zeilensummen
    dynamic_table = [header]
    column_totals = defaultdict(int)
    overall_total = 0

    for order_id in sorted(order_totals.keys()):
        row = [order_id]
        row_total = 0
        for product in sorted_product_names:
            count = order_totals[order_id][product]
            row.append(count)
            row_total += count
            column_totals[product] += count
        row.append(row_total)
        overall_total += row_total
        dynamic_table.append(row)

    # Füge die Spaltensummen hinzu
    total_row = ["Total"]
    for product in sorted_product_names:
        total_row.append(column_totals[product])
    total_row.append(overall_total)

    dynamic_table.append(total_row)

    return dynamic_table
