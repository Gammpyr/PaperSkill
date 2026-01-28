import os

import stripe

stripe.api_key = os.getenv("STRIPE_API_KEY")


def create_stripe_product(product_name):
    """Создаёт продукт в Stripe"""
    product = stripe.Product.create(name=f"Курс {product_name}")

    return product


def create_stripe_price(product, amount):
    """Создаёт цену в Stripe"""
    # product_id = stripe.Product.retrieve(product_id)
    price = stripe.Price.create(
        currency="rub",
        unit_amount=int(amount * 100),
        product_data={"name": product.get("name")},
    )

    return price


def create_stripe_session(price, success_url, cancel_url):
    """Создаёт сессию в Stripe"""
    session = stripe.checkout.Session.create(
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
        line_items=[{"price": price.get("id"), "quantity": 1}],
        mode="payment",
        payment_method_types=["card"],
    )
    return session


def check_payment_status(session_id):
    """Проверяет статус платежа"""
    session = stripe.checkout.Session.retrieve(session_id)
    return session.payment_status
