from flask import (
    Blueprint,
    g,
    session,
    render_template,
    request,
    flash,
    redirect,
    url_for,
)

from src.app.controllers.cart import CartController
from src.app.controllers.order_item import OrderItemController
from src.app.controllers.orders import OrderController
from src.app.controllers.product import ProductController
from src.app.routes.user import login_required

remove_from_cart_blueprint = Blueprint(
    "remove_from_cart", __name__, url_prefix="/remove-from-cart"
)
cart_blueprint = Blueprint("cart", __name__, url_prefix="/cart")
add_item_cart_blueprint = Blueprint("add_item", __name__, url_prefix="/add-to-cart")
checkout_blueprint = Blueprint("checkout", __name__, url_prefix="/checkout")


def update_cart_item_count(user_id: int) -> None:
    ses = g.session
    item_count = CartController(ses).count_items(user_id)
    session["no_of_items"] = item_count


@remove_from_cart_blueprint.route("/")
@login_required
def remove_from_cart():
    product_id = int(request.args.get("productId"))

    try:
        ses = g.session
        CartController(ses).remove_product_from_user_cart(
            session["user_id"], product_id
        )
        update_cart_item_count(session["user_id"])
        flash("Item removed successfully", "info")
    except Exception as e:
        flash(f"Error removing item from cart: {e}", "error")

    return redirect(url_for("root.root"))


@add_item_cart_blueprint.route("/")
@login_required
def add_to_cart():
    product_id = int(request.args.get("productId"))
    user_id = session["user_id"]

    try:
        ses = g.session
        CartController(ses).add_item_for_user(user_id, product_id)
        update_cart_item_count(user_id)
        flash("Item added successfully", "info")
    except Exception as e:
        flash(f"Error adding item from cart: {e}", "error")

    return redirect(url_for("root.root"))


@checkout_blueprint.route("/")
@login_required
def checkout():
    user_id = session["user_id"]
    ses = g.session
    cart_with_product_info = CartController(ses).get_order_with_product_info(user_id)

    total = sum(order_item["total"] for order_item in cart_with_product_info)

    try:
        order_id = OrderController(ses).insert_order_by_user_id(user_id, total)

        for order_item in cart_with_product_info:
            OrderItemController(ses).add_order_item(
                order_id, order_item["product_id"], order_item["quantity"]
            )
            ProductController(ses).update_stock_for_product(
                order_item["product_id"], order_item["quantity"]
            )

        CartController(ses).clear_cart_by_user_id(user_id)
        update_cart_item_count(user_id)

        flash("Order successful", "info")
    except Exception as e:
        flash(f"Error on checkout: {e}", "error")

    return redirect(url_for("root.root"))


@cart_blueprint.route("/")
@login_required
def cart():
    ses = g.session
    cart_with_product_info = CartController(ses).get_cart_with_product_info_by_user_id(
        session["user_id"]
    )
    total_price = calculate_product_sum_with_discount_util(cart_with_product_info)

    return render_template(
        "cart.html",
        products=cart_with_product_info,
        totalPrice=total_price,
        loggedIn=session["logged_in"],
        firstName=session["first_name"],
        noOfItems=session["no_of_items"],
    )


def get_prices_from_cart(products: list[dict[str, int | str]]) -> list[int]:
    prices: list[int] = []

    for product in products:
        prices.append(product["price"])

    return prices


def calculate_product_sum_with_discount_util(
    products: list[dict[str, int | str]]
) -> int:
    prices = get_prices_from_cart(products)

    # TODO: Implementieren eines speziellen Rabattes, der die Summe des neuen Warenkorbs berechnet
    total_price = 0
    for price in prices:
        found_smaller_value = False
        for new_value in prices:
            if price >= new_value:
                total_price += price - new_value
                found_smaller_value = True
        if found_smaller_value == False:
            total_price += price
            found_smaller_value = False
    return total_price
