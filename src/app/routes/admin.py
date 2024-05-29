from flask import Blueprint, session, redirect, url_for, render_template, flash, g

from src.app.controllers import OrderController
from src.app.routes.user import login_required

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

    # TODO: Code zum fixen des Tests verstehen und Codequalität verbessern
    if orders == []:
        return orders

    allProductNames: list[str] = []
    allOrders: dict[int, dict[str, int]] = {}
    current_item: str = ""

    for order_item_id, order_id, product_name in orders:
        # Collect unique product names for column headers
        if product_name not in allProductNames:
            allProductNames.append(product_name)

        # Counts the number of each product_name in the order per order_id
        if order_id in allOrders:
            if product_name in allOrders[order_id]:
                allOrders[order_id][product_name] = (
                    allOrders[order_id][product_name] + 1
                )
            elif product_name not in allOrders[order_id]:
                allOrders[order_id][product_name] = 1
        else:
            allOrders[order_id] = {product_name: 1}
    print(allOrders)
    # Sort column headers in lexicographical  order (by chars in unicode value range) ascending
    allProductNames = sorted(allProductNames)
    all_column_headers: list[int] = ["Order ID"] + [d for d in allProductNames]

    dynamic_table: list[list[str | int]] = []
    dynamic_table.append(all_column_headers)

    # Fill 2d array with values, where column headers are product name and row headers are order id
    for row_order_id in sorted(
        allOrders, key=int
    ):  # int to sort tables ascending by order_id
        list_: list[any] = []
        list_.append((row_order_id))
        for i in range(1, len(all_column_headers)):
            current_product: str = all_column_headers[i]
            if current_product in allOrders[row_order_id]:
                list_.append(allOrders[row_order_id][current_product])
            else:
                list_.append(0)
        dynamic_table.append(list_)

    print("dynamic table:")
    print(dynamic_table)

    # for row in dynamicTable:
    #    print(row)

    dynamic_table[0].append("Total")

    for row in dynamic_table[1:]:
        sum01 = sum(row[1:])
        row.append(sum01)

    empty_list = ["Total"]
    row_total = [empty_list.append(sum(x)) for x in zip(*dynamic_table[1:])]
    return row_total
    return dynamic_table if not len(dynamic_table) <= 1 else []
