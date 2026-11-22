WAITING_FOR_PIZZA_TYPE = "waiting_for_pizza_type"
WAITING_FOR_PIZZA_SIZE = "waiting_for_pizza_size"
WAITING_FOR_DRINK = "waiting_for_drink"
FINISHED = "finished"

PIZZA_PROMPT = "Выберите пиццу"
SIZE_PROMPT = "Выберите размер"
DRINK_PROMPT = "Выберите напиток"

PIZZAS: tuple[tuple[str, str], ...] = (
    ("margherita", "Маргарита"),
    ("pepperoni", "Пепперони"),
    ("four_cheese", "Четыре сыра"),
    ("hawaiian", "Гавайская"),
    ("napoletano", "Неаполетано"),
)

SIZES: tuple[tuple[str, str], ...] = (
    ("small", "Маленькая (25 см)"),
    ("medium", "Средняя (33 см)"),
    ("large", "Большая (40 см)"),
)

DRINKS: tuple[tuple[str, str], ...] = (
    ("juice", "Сок"),
    ("mors", "Морс"),
    ("tea", "Чай"),
    ("cola", "Кола"),
    ("none", "Без напитка"),
)


def inline_keyboard(
    options: tuple[tuple[str, str], ...],
) -> dict[str, list[list[dict[str, str]]]]:
    return {
        "inline_keyboard": [
            [{"text": label, "callback_data": slug}] for slug, label in options
        ]
    }


def choice(options: tuple[tuple[str, str], ...], slug: str | None) -> str | None:
    if slug is None:
        return None
    for value, _label in options:
        if value == slug:
            return value
    return None


def format_order(order: dict[str, str]) -> str:
    return (
        "Заказ оформлен:\n"
        f"Пицца: {_label(PIZZAS, order.get('type', ''))}\n"
        f"Размер: {_label(SIZES, order.get('size', ''))}\n"
        f"Напиток: {_label(DRINKS, order.get('drink', ''))}"
    )


def _label(options: tuple[tuple[str, str], ...], slug: str) -> str:
    for value, label in options:
        if value == slug:
            return label
    return slug
