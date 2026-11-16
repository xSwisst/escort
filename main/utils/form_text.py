from bot.assets.texts import t


def _format_price(price: int | None, discount_amount: int | None = None) -> str:
    if not price:
        return "<b>Не указана</b>"
    if discount_amount:
        discounted = max(int(price) - int(discount_amount), 0)
        return f"<s>{price}</s> <b>{discounted}</b>"
    return f"<b>{price}</b>"


def build_form_text(form, *, cta: bool = False, discount_amount: int | None = None) -> str:
    discount = discount_amount if discount_amount is not None else getattr(form, "discount_amount", None)

    one_hour = _format_price(getattr(form, "one_hour_price", None), discount)
    two_hours = _format_price(getattr(form, "two_hour_price", None), discount)
    three_hours = _format_price(getattr(form, "three_hour_price", None), discount)
    overnight = _format_price(getattr(form, "overnight_price", None), discount)

    caption = str(getattr(form, "caption", "") or "").strip() or "У анкеты нет описания"

    verification = "<b>Пройдена</b>" if getattr(form, "is_verified", False) else "<b>Не пройдена</b>"
    medical_certificate = "<b>Актуальна</b>" if getattr(form, "has_medical_certificate", False) else "<b>Неактуальна</b>"

    rating_val = getattr(form, "rating", None)
    if rating_val is not None and float(rating_val) > 0:
        rating = f"<b>{float(rating_val):.1f}</b>"
    else:
        rating = "<b>У модели нет рейтинга</b>"

    orders_val = getattr(form, "orders", None)
    if orders_val is not None and int(orders_val) > 0:
        orders = f"<b>{int(orders_val)}</b>"
    else:
        orders = "<b>У модели нет заказов</b>"

    return t(
        "model_card",
        name=form.name,
        age=form.age,
        one_hour_price=one_hour,
        two_hour_price=two_hours,
        three_hour_price=three_hours,
        overnight_price=overnight,
        height=form.height,
        bust_size=form.bust_size,
        caption=caption,
        verification=verification,
        medical_certificate=medical_certificate,
        rating=rating,
        orders=orders,
    )
