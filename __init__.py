# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.request import urlopen
from xml.etree import ElementTree

import albert
import inflect
import pint

default_trigger = "convert "
synopsis = "<amount> <from_unit> to <to_unit>"

__doc__ = f"""
Extension for converting units of length, mass, speed, temperature, time,
current, luminosity, printing measurements, molecular substance, currency, and more

Synopsis: {default_trigger}{synopsis}

Examples:
`{default_trigger}180 minutes to hrs`
`{default_trigger}100 km to miles`
`{default_trigger}88 mph to kph`
`{default_trigger}32 degrees F to C`
`{default_trigger}3.14159 rad to degrees`
`{default_trigger}100 USD to EUR`
"""

md_iid = "0.5"
md_version = "1.1"
md_name = "Unit Converter"
md_description = "Convert length, mass, temperature, time, currency, and more"
md_license = "MIT"
md_url = "https://github.com/DenverCoder1/unit-converter-albert-ext"
md_lib_dependencies = ["pint", "inflect"]
md_maintainers = "@DenverCoder1"

unit_convert_regex = re.compile(
    r"(?P<from_amount>-?\d+\.?\d*)\s?(?P<from_unit>.*)\s(?:to|in)\s(?P<to_unit>.*)",
    re.I,
)

units = pint.UnitRegistry()
inflect_engine = inflect.engine()


def load_config(config_path: Path) -> dict[str, Any]:
    """
    Strip comments and load the config from the config file.
    """
    with config_path.open("r") as config_file:
        contents = config_file.read()
    contents = re.sub(r"^\s*//.*$", "", contents, flags=re.MULTILINE)
    return json.loads(contents)


config_path = Path(__file__).parent / "config.jsonc"
config = load_config(config_path)


class ConversionResult:
    """
    A class to represent the result of a unit conversion
    """

    def __init__(
        self,
        from_amount: float,
        from_unit: str,
        to_amount: float,
        to_unit: str,
        dimensionality: str,
    ):
        """
        Initialize the ConversionResult

        Args:
            from_amount (float): The amount to convert from
            from_unit (str): The unit to convert from
            to_amount (float): The resulting amount
            to_unit (str): The unit converted to
            dimensionality (str): The dimensionality of the result
        """
        self.from_amount = from_amount
        self.from_unit = from_unit
        self.to_amount = to_amount
        self.to_unit = to_unit
        self.dimensionality = dimensionality
        self.display_names = config.get("display_names", {})
        self.rounding_precision = int(config.get("rounding_precision", 3))
        self.rounding_precision_zero = int(config.get("rounding_precision_zero", 12))

    def __pluralize_unit(self, unit: str) -> str:
        """
        Pluralize the unit

        Args:
            unit (str): The unit to pluralize

        Returns:
            str: The pluralized unit
        """
        # if all characters are uppercase, don't pluralize
        if unit.isupper():
            return unit
        return inflect_engine.plural(unit)

    def __display_unit_name(self, amount: float, unit: str) -> str:
        """
        Display the name of the unit with plural if necessary

        Args:
            unit (str): The unit to display

        Returns:
            str: The name of the unit
        """
        unit = self.__pluralize_unit(unit) if amount != 1 else unit
        return self.display_names.get(unit, unit)

    def __format_float(self, num: float) -> str:
        """
        Format a float to remove trailing zeros and avoid scientific notation

        Args:
            num (float): The number to format

        Returns:
            str: The formatted number
        """
        # if rounding precision is -1, leave as is
        if self.rounding_precision == -1:
            return str(num)
        # round to the given rounding precision
        rounded = round(num, self.rounding_precision)
        # if it is close to zero, round to the given precision for zero
        if rounded == 0 and self.rounding_precision_zero > 0:
            zero_delta = 1 / 10 ** self.rounding_precision_zero
            if abs(num) > zero_delta:
                rounded = round(num, self.rounding_precision_zero)
        # format the float to remove trailing zeros and decimal point
        return f"{rounded:f}".rstrip("0").rstrip(".")

    @property
    def formatted_result(self) -> str:
        """
        Return the formatted result amount and unit
        """
        units = self.__display_unit_name(self.to_amount, self.to_unit)
        return f"{self.__format_float(self.to_amount)} {units}"

    @property
    def formatted_from(self) -> str:
        """
        Return the formatted from amount and unit
        """
        units = self.__display_unit_name(self.from_amount, self.from_unit)
        return f"{self.__format_float(self.from_amount)} {units}"

    @property
    def icon(self) -> str:
        """
        Return the icon for the result's dimensionality
        """
        # strip characters from the dimensionality if not alphanumeric or underscore
        dimensionality = re.sub(r"[^\w]", "", self.dimensionality)
        return f"{dimensionality}.svg"

    def __repr__(self):
        """
        Return the representation of the result
        """
        return f"{self.formatted_from} = {self.formatted_result}"


class UnitConverter:
    def __init__(self):
        """
        Initialize the UnitConverter
        """
        self.aliases: dict[str, str] = config.get("aliases", {})

    def _get_unit(self, unit: str) -> pint.Unit:
        """
        Check if the unit is a valid unit and return it
        If any aliases are found, replace the unit with the alias
        If the unit is not valid, check if making it lowercase will fix it
        If not, raise the UndefinedUnitError

        Args:
            unit (str): The unit to check

        Returns:
            pint.Unit: The unit

        Raises:
            pint.errors.UndefinedUnitError: If the unit is not valid
        """
        unit = self.aliases.get(unit, unit)
        if units.__contains__(unit):
            # return the unit if it is valid
            return units.__getattr__(unit)
        # check if the lowercase version is a valid unit
        return units.__getattr__(unit.lower())

    def convert_units(self, amount: float, from_unit: str, to_unit: str) -> ConversionResult:
        """
        Convert a unit to another unit

        Args:
            amount (float): The amount to convert
            from_unit (str): The unit to convert from
            to_unit (str): The unit to convert to

        Returns:
            str: The resulting amount in the new unit

        Raises:
            pint.errors.UndefinedUnitError: If the unit is not valid
            pint.errors.DimensionalityError: If the units are not compatible
        """
        input_unit = units.Quantity(amount, self._get_unit(from_unit))
        output_unit = self._get_unit(to_unit)
        result = input_unit.to(output_unit)
        return ConversionResult(
            from_amount=float(amount),
            from_unit=str(self._get_unit(from_unit)),
            to_amount=result.magnitude,
            to_unit=str(result.units),
            dimensionality=str(units._get_dimensionality(result.units)),
        )


class UnknownCurrencyError(Exception):
    def __init__(self, currency: str):
        """
        Initialize the UnknownCurrencyError

        Args:
            currency (str): The unknown currency
        """
        self.currency = currency
        super().__init__(f"Unknown currency: {currency}")


class CurrencyConverter:

    API_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"

    def __init__(self):
        """
        Initialize the CurrencyConverter
        """
        self.last_update = datetime.now()
        self.aliases: dict[str, str] = config.get("aliases", {})
        self.currencies = self._get_currencies()

    def _get_currencies(self) -> dict[str, float]:
        """
        Get the currencies from the API

        Returns:
            dict[str, float]: The currencies
        """
        with urlopen(self.API_URL) as response:
            xml = response.read().decode("utf-8").strip()
        root = ElementTree.fromstring(xml)
        currency_cube = root[-1][0]
        if currency_cube is None:
            albert.warning("Could not find currencies in XML")
            return {}
        currencies = {
            currency.attrib["currency"]: float(currency.attrib["rate"])
            for currency in currency_cube
        }
        currencies["EUR"] = 1
        albert.info(f"Loaded currencies: {currencies}")
        return currencies

    def normalize_currency(self, currency: str) -> str | None:
        """
        Get the currency name normalized using aliases

        Args:
            currency (str): The currency to normalize

        Returns:
            Optional[str]: The currency name or None if not found
        """
        currency = self.aliases.get(currency, currency).upper()
        return currency if currency in self.currencies else None

    def convert_currency(
        self, amount: float, from_currency: str, to_currency: str
    ) -> ConversionResult:
        """
        Convert a currency to another currency

        Args:
            amount (float): The amount to convert
            from_currency (str): The currency to convert from
            to_currency (str): The currency to convert to

        Returns:
            str: The resulting amount in the new currency

        Raises:
            UnknownCurrencyError: If the currency is not valid
        """
        # update the currencies every 24 hours
        if (datetime.now() - self.last_update).days >= 1:
            self.currencies = self._get_currencies()
            self.last_update = datetime.now()
        # get the currency rates
        from_unit = self.normalize_currency(from_currency)
        to_unit = self.normalize_currency(to_currency)
        # convert the currency
        if from_unit is None:
            raise UnknownCurrencyError(from_currency)
        if to_unit is None:
            raise UnknownCurrencyError(to_currency)
        from_rate = self.currencies[from_unit]
        to_rate = self.currencies[to_unit]
        result = amount * to_rate / from_rate
        return ConversionResult(
            from_amount=float(amount),
            from_unit=from_unit,
            to_amount=result,
            to_unit=to_unit,
            dimensionality="currency",
        )


class Plugin(albert.QueryHandler):
    def initialize(self):
        """Initialize the plugin."""
        self.unit_converter = UnitConverter()
        self.currency_converter = CurrencyConverter()

    def id(self) -> str:
        return __name__

    def name(self) -> str:
        return md_name

    def description(self) -> str:
        return md_description

    def synopsis(self) -> str:
        return synopsis

    def defaultTrigger(self) -> str:
        return default_trigger

    def handleQuery(self, query: albert.Query) -> None:
        """Handler for a query received from Albert."""
        query_string = query.string.strip()
        match = unit_convert_regex.fullmatch(query_string)
        if match:
            albert.info(f"Matched {query_string}")
            try:
                items = self.get_items(
                    float(match.group("from_amount")),
                    match.group("from_unit").strip(),
                    match.group("to_unit").strip(),
                )
                query.add(items)
            except Exception as error:
                albert.warning(f"Error: {error}")
                tb = "".join(
                    traceback.format_exception(error.__class__, error, error.__traceback__)
                )
                albert.warning(tb)
                albert.info("Something went wrong. Make sure you're using the correct format.")

    def create_item(self, text: str, subtext: str, icon: str = "") -> albert.Item:
        """
        Create an albert.Item from a text and subtext

        Args:
            text (str): The text to display
            subtext (str): The subtext to display
            icon (Optional[str]): The icon to display. If not specified, the default icon will be used

        Returns:
            albert.Item: The item to be added to the list of results
        """
        icon_path = Path(__file__).parent / "icons" / icon
        if not icon or not icon_path.exists():
            albert.warning(f"Icon {icon} does not exist")
            icon_path = Path(__file__).parent / "icons" / "unit_converter.svg"
        return albert.Item(
            id=str(icon_path),
            icon=[str(icon_path)],
            text=text,
            subtext=subtext,
            actions=[
                albert.Action(
                    id="copy",
                    text="Copy result to clipboard",
                    callable=lambda: albert.setClipboardText(text=text),
                )
            ],
        )

    def get_items(self, amount: float, from_unit: str, to_unit: str) -> list[albert.Item]:
        """
        Generate the Albert items to display for the query

        Args:
            amount (float): The amount to convert from
            from_unit (str): The unit to convert from
            to_unit (str): The unit to convert to

        Returns:
            List[albert.Item]: The list of items to display
        """
        try:
            # convert currencies
            if (
                self.currency_converter.normalize_currency(from_unit) is not None
                and self.currency_converter.normalize_currency(to_unit) is not None
            ):
                result = self.currency_converter.convert_currency(amount, from_unit, to_unit)
            # convert standard units
            else:
                result = self.unit_converter.convert_units(amount, from_unit, to_unit)
            # return the result
            return [
                self.create_item(
                    result.formatted_result,
                    f"Converted from {result.formatted_from}",
                    result.icon,
                )
            ]
        except pint.errors.DimensionalityError as e:
            albert.warning(f"DimensionalityError: {e}")
            albert.warning(traceback.format_exc())
            return [
                self.create_item(f"Unable to convert {amount} {from_unit} to {to_unit}", str(e))
            ]
        except pint.errors.UndefinedUnitError as e:
            albert.warning(f"UndefinedUnitError: {e}")
            albert.warning(traceback.format_exc())
            return []
        except UnknownCurrencyError as e:
            albert.warning(f"UnknownCurrencyError: {e}")
            albert.warning(traceback.format_exc())
            return []
