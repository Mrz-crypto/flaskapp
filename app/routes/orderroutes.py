from flask import Blueprint
from app.controllers import ordercontroller

bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.route("/", methods=["GET"])
def list_orders():
    return ordercontroller.list_orders()


@bp.route("/<int:order_id>", methods=["GET"])
def get_order(order_id):
    return ordercontroller.get_order(order_id)


@bp.route("/", methods=["POST"])
def create_order():
    return ordercontroller.create_order_api()


@bp.route("/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    return ordercontroller.update_order(order_id)


@bp.route("/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    return ordercontroller.delete_order(order_id)


def register_blueprint():
    return bp
