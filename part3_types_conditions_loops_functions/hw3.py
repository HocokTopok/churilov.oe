#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

DATE_PARTS_COUNT = 3
DAY_DIGITS = 2
MONTH_DIGITS = 2
YEAR_DIGITS = 4
MONTHS_IN_YEAR = 12
INCOME_ARGS = 3
COST_ARGS = 4
STATS_ARGS = 2
FEB_INDEX = 2
FEB_LEAP_DAYS = 29
CATEGORY_PARTS_COUNT = 2
COST_CATEGORIES_ARGS = 2


EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    divisible_by_four = year % 4 == 0
    divisible_by_one_hundred = year % 100 == 0
    divisible_by_four_hundred = year % 400 == 0

    if not divisible_by_four:
        return False

    return not (divisible_by_one_hundred and not divisible_by_four_hundred)


def _check_lengths(parts: list[str]) -> bool:
    if len(parts) != DATE_PARTS_COUNT:
        return False
    day, month, year = parts
    day_ok = len(day) == DAY_DIGITS
    month_ok = len(month) == MONTH_DIGITS
    year_ok = len(year) == YEAR_DIGITS
    return day_ok and month_ok and year_ok


def _are_digits(parts: list[str]) -> bool:
    return all(part.isdigit() for part in parts)


def _build_days_in_month(year: int, month: int) -> int:
    month_days = [31, 30, 31, 31, 30, 31, 30, 31]
    days_in_month = [0, 31, 28, 31, 30, *month_days]
    if is_leap_year(year):
        days_in_month[FEB_INDEX] = FEB_LEAP_DAYS
    return days_in_month[month]


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parts = maybe_dt.split("-")
    if not _check_lengths(parts):
        return None

    if not _are_digits(parts):
        return None

    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])

    if day < 1 or month < 1 or month > MONTHS_IN_YEAR or year < 1:
        return None

    days_in_month = _build_days_in_month(year, month)
    if day > days_in_month:
        return None

    return (day, month, year)


def _validate_category(maybe_cg: str) -> bool:
    parts = maybe_cg.split("::")
    if len(parts) != CATEGORY_PARTS_COUNT:
        return False
    common, target = parts
    if common not in EXPENSE_CATEGORIES:
        return False
    return target in EXPENSE_CATEGORIES[common]


def _parse_raw_amount(raw: str) -> float:
    return float(raw.replace(",", "."))


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    date = extract_date(income_date)
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append({"type": "income", "amount": amount, "date": date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    date = extract_date(income_date)
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    if not _validate_category(category_name):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    financial_transactions_storage.append({"type": "cost", "category": category_name, "amount": amount, "date": date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    lines: list[str] = []
    for common, targets in EXPENSE_CATEGORIES.items():
        lines.extend(f"{common}::{target}" for target in targets)
    return "\n".join(lines)


def _is_in_period(date: tuple[int, int, int], query_year: int, query_month: int) -> bool:
    _, month, year = date
    return year == query_year and month == query_month


def _format_categories(costs: dict[str, float]) -> list[str]:
    lines: list[str] = []
    sorted_items = sorted(costs.items(), key=lambda item: item[0])
    for index, (category, value) in enumerate(sorted_items, 1):
        printable_value = int(value) if value == int(value) else value
        lines.append(f"{index}. {category}: {printable_value}")
    return lines


def _build_stats_lines(
    capital: float,
    month_income: float,
    month_cost: float,
    costs: dict[str, float],
    report_date: str,
) -> list[str]:
    budget = month_income - month_cost
    direction = "loss" if budget < 0 else "profit"
    lines: list[str] = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {capital:.2f} rubles",
        f"This month, the {direction} amounted to {abs(budget):.2f} rubles.",
        f"Income: {month_income:.2f} rubles",
        f"Expenses: {month_cost:.2f} rubles",
        "",
        "Details (category: amount):",
    ]
    lines.extend(_format_categories(costs))
    return lines


def _to_comparable(date: tuple[int, int, int]) -> tuple[int, int, int]:
    day, month, year = date
    return (year, month, day)


def _helper_start_handler(
    rec: dict[str, Any],
    query_date: tuple[int, int, int],
    accum: list[float],
    costs: dict[str, float],
) -> None:
    date = rec["date"]
    if _to_comparable(date) > _to_comparable(query_date):
        return
    _, query_month, query_year = query_date
    amount = rec["amount"]
    if rec["type"] == "income":
        accum[0] += amount
        if _is_in_period(date, query_year, query_month):
            accum[1] += amount
    else:
        accum[0] -= amount
        if _is_in_period(date, query_year, query_month):
            accum[2] += amount
            category = rec["category"]
            costs[category] = costs.get(category, 0) + amount


def _collect_stats(
    query_date: tuple[int, int, int],
) -> tuple[list[float], dict[str, float]]:
    accum: list[float] = [float(0), float(0), float(0)]
    costs: dict[str, float] = {}
    for rec in financial_transactions_storage:
        _helper_start_handler(rec, query_date, accum, costs)
    return accum, costs


def _format_stats(accum: list[float], costs: dict[str, float], report_date: str) -> str:
    capital, month_income, month_cost = accum
    lines = _build_stats_lines(capital, month_income, month_cost, costs, report_date)
    return "\n".join(lines)


def stats_handler(report_date: str) -> str:
    query_date = extract_date(report_date)
    if query_date is None:
        return INCORRECT_DATE_MSG
    accum, costs = _collect_stats(query_date)
    return _format_stats(accum, costs, report_date)


def _handle_income(parts: list[str]) -> None:
    if len(parts) != INCOME_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = _parse_raw_amount(parts[1])
    raw_date = parts[2]

    if amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    if extract_date(raw_date) is None:
        print(INCORRECT_DATE_MSG)
        return

    print(income_handler(amount, raw_date))


def _handle_cost(parts: list[str]) -> None:
    if len(parts) == COST_CATEGORIES_ARGS and parts[1] == "categories":
        print(cost_categories_handler())
        return

    if len(parts) != COST_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    raw_category = parts[1]
    amount = _parse_raw_amount(parts[2])
    raw_date = parts[3]

    if amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return

    if extract_date(raw_date) is None:
        print(INCORRECT_DATE_MSG)
        return

    if not _validate_category(raw_category):
        print(NOT_EXISTS_CATEGORY)
        print(cost_categories_handler())
        return

    print(cost_handler(raw_category, amount, raw_date))


def _handle_stats(parts: list[str]) -> None:
    if len(parts) != STATS_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(stats_handler(parts[1]))


def main() -> None:
    handlers = {
        "income": _handle_income,
        "cost": _handle_cost,
        "stats": _handle_stats,
    }
    line = input()
    while line:
        parts = line.split()
        if parts:
            handler = handlers.get(parts[0])
            if handler:
                handler(parts)
            else:
                print(UNKNOWN_COMMAND_MSG)
        line = input()


if __name__ == "__main__":
    main()
