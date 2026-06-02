from flask import Blueprint
from app.controllers import ordercontroller

bp = Blueprint('orders', __name__, url_prefix='/orders')

def register():
    bp.route('/', methods=['GET'])(ordercontroller.list_orders)
    bp.route('/<int:order_id>', methods=['GET'])(ordercontroller.get_order)
    bp.route('/', methods=['POST'])(ordercontroller.create_order)
    bp.route('/<int:order_id>', methods=['PUT'])(ordercontroller.update_order)
    bp.route('/<int:order_id>', methods=['DELETE'])(ordercontroller.delete_order)
    return bp
