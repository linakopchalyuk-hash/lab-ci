from unittest.mock import Mock

import pytest

from shop.cart import Cart

# 1. Базові тести


def test_empty_cart(cart: Cart) -> None:
    assert cart.items_count() == 0


def test_add_one_item(cart: Cart) -> None:
    cart.add("book", 200.0)
    assert cart.items_count() == 1


def test_add_multiple_items(cart: Cart) -> None:
    cart.add("book", 200.0, 2)
    cart.add("pen", 15.0, 3)
    assert cart.items_count() == 5


def test_add_same_item_twice(cart: Cart) -> None:
    cart.add("book", 200.0, 2)
    cart.add("book", 200.0, 3)
    assert cart.items_count() == 5


def test_remove_item(cart: Cart) -> None:
    cart.add("book", 200.0)
    cart.remove("book")
    assert cart.items_count() == 0


def test_items_count(cart_with_items: Cart) -> None:
    assert cart_with_items.items_count() == 6


def test_total(cart_with_items: Cart) -> None:
    assert cart_with_items.total() == 460.0


# 2. Параметризовані тести знижок


@pytest.mark.parametrize(
    ("discount", "expected"),
    [
        (0, 400.0),
        (10, 360.0),
        (25, 300.0),
        (50, 200.0),
        (75, 100.0),
        (100, 0.0),
    ],
)
def test_total_with_discount(
    cart: Cart,
    discount: float,
    expected: float,
) -> None:
    cart.add("book", 200.0, 2)
    assert cart.total(discount) == expected


# 3. Перевірка винятків


def test_negative_price_raises(cart: Cart) -> None:
    with pytest.raises(ValueError, match="price"):
        cart.add("book", -10.0)


def test_zero_quantity_raises(cart: Cart) -> None:
    with pytest.raises(ValueError, match="qty"):
        cart.add("book", 200.0, 0)


def test_negative_quantity_raises(cart: Cart) -> None:
    with pytest.raises(ValueError, match="qty"):
        cart.add("book", 200.0, -1)


def test_invalid_discount_raises(cart: Cart) -> None:
    with pytest.raises(ValueError, match="discount_percent"):
        cart.total(150)


def test_negative_discount_raises(cart: Cart) -> None:
    with pytest.raises(ValueError, match="discount_percent"):
        cart.total(-10)


def test_remove_missing_item_raises(cart: Cart) -> None:
    with pytest.raises(KeyError):
        cart.remove("phone")


# 4. Тестування конвертації валюти через Mock


def test_total_in_usd(cart: Cart) -> None:
    rates = Mock()
    rates.get_rate.return_value = 40.0

    cart.add("book", 400.0)

    result = cart.total_in("USD", rates)

    assert result == 10.0
    rates.get_rate.assert_called_once_with("USD")


def test_total_in_with_multiple_items(cart: Cart) -> None:
    rates = Mock()
    rates.get_rate.return_value = 40.0

    cart.add("book", 200.0, 2)
    cart.add("pen", 20.0, 2)

    assert cart.total_in("USD", rates) == 11.0


def test_invalid_exchange_rate_raises(cart: Cart) -> None:
    rates = Mock()
    rates.get_rate.return_value = 0.0

    with pytest.raises(ValueError, match="rate"):
        cart.total_in("USD", rates)


def test_negative_exchange_rate_raises(cart: Cart) -> None:
    rates = Mock()
    rates.get_rate.return_value = -5.0

    with pytest.raises(ValueError, match="rate"):
        cart.total_in("USD", rates)


# 5. Повторне додавання товару з іншою ціною


def test_add_same_name_with_different_price(cart: Cart) -> None:
    cart.add("book", 200.0, 1)
    cart.add("book", 300.0, 1)

    assert cart.items_count() == 2
    assert cart.total() == 400.0


# 6. TDD: метод most_expensive()


def test_most_expensive_empty_cart(cart: Cart) -> None:
    assert cart.most_expensive() is None


def test_most_expensive_single_item(cart: Cart) -> None:
    cart.add("book", 200.0)
    result = cart.most_expensive()

    assert result is not None
    assert result.name == "book"


def test_most_expensive_multiple_items(cart: Cart) -> None:
    cart.add("book", 200.0, 2)
    cart.add("phone", 1000.0)
    cart.add("pen", 15.0, 4)

    result = cart.most_expensive()

    assert result is not None
    assert result.name == "phone"


def test_most_expensive_uses_unit_price(cart: Cart) -> None:
    cart.add("book", 200.0, 10)
    cart.add("phone", 1000.0, 1)

    result = cart.most_expensive()

    assert result is not None
    assert result.name == "phone"
