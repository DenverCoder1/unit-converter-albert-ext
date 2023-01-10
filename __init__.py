# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import re
import traceback
from pathlib import Path

import albert
import pint
import inflect

__doc__ = """
Extension for converting units of length, mass, speed, temperature, time,
current, luminosity, printing measurements, molecular substance, and more

Synopsis: `<from_amount> <from_unit> {to|in} <to_unit>`

Examples:
`180 minutes to hrs`
`100 km in miles`
`88 mph in kph`
`32 degrees F to C`
`3.14159 rad to degrees`
"""

md_iid = "0.5"
md_version = "1.0"
md_name = "Unit Converter"
md_description = "Convert length, mass, speed, temperature, time, and more"
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


def load_config(config_path: Path) -> dict[str, dict[str, str]]:
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
        from_unit: pint.Unit,
        to_amount: float,
        to_unit: pint.Unit,
    ):
        """
        Initialize the ConversionResult

        Args:
            from_amount (float): The amount to convert from
            from_unit (Unit): The unit to convert from
            to_amount (float): The resulting amount
            to_unit (Unit): The unit converted to
        """
        self.from_amount = from_amount
        self.from_unit = from_unit
        self.to_amount = to_amount
        self.to_unit = to_unit
        self.dimensionality = units._get_dimensionality(to_unit)
        self.display_names = config.get("display_names", {})

    def __pluralize_unit(self, unit: pint.Unit) -> str:
        """
        Pluralize the unit

        Args:
            unit (Unit): The unit to pluralize

        Returns:
            str: The pluralized unit
        """
        return inflect_engine.plural(str(unit))

    def __display_unit_name(self, amount: float, unit: pint.Unit) -> str:
        """
        Display the name of the unit with plural if necessary

        Args:
            unit (Unit): The unit to display

        Returns:
            str: The name of the unit
        """
        unit = self.__pluralize_unit(unit) if amount != 1 else str(unit)
        return self.display_names.get(unit, unit)

    def __round_or_truncate(self, num: float) -> float | int:
        """
        Round floating point number to 2 decimal places or convert to an integer if ends with .0

        Args:
            num (float): The number to round

        Returns:
            Union[float, int]: The rounded number
        """
        return round(num, 2) if num % 1 else int(num)

    @property
    def formatted_result(self) -> str:
        """
        Return the formatted result amount and unit
        """
        units = self.__display_unit_name(self.to_amount, self.to_unit)
        return f"{self.__round_or_truncate(float(self.to_amount))} {units}"

    @property
    def formatted_from(self) -> str:
        """
        Return the formatted from amount and unit
        """
        units = self.__display_unit_name(self.from_amount, self.from_unit)
        return f"{self.__round_or_truncate(float(self.from_amount))} {units}"

    @property
    def icon(self) -> str:
        """
        Return the icon for the result's dimensionality
        """
        # strip characters from the dimensionality if not alphanumeric or underscore
        dimensionality = re.sub(r"[^\w]", "", str(self.dimensionality))
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
            from_unit=self._get_unit(from_unit),
            to_amount=result.magnitude,
            to_unit=result.units,
        )


class Plugin(albert.QueryHandler):
    def id(self) -> str:
        return __name__

    def name(self) -> str:
        return md_name

    def description(self) -> str:
        return md_description

    def synopsis(self) -> str:
        return "<from_amount> <from_unit> {to|in} <to_unit>" if self.defaultTrigger() else ""

    def defaultTrigger(self) -> str:
        return ""

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
            id=self.name(),
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
        uc = UnitConverter()
        try:
            # convert the units
            result = uc.convert_units(amount, from_unit, to_unit)
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
