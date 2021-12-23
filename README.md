# unit-converter-albert-ext

[![discord](https://custom-icon-badges.herokuapp.com/discord/819650821314052106?color=5865F2&logo=discord-outline&logoColor=white "Dev Pro Tips Discussion & Support Server")](https://discord.gg/fPrdqh3Zfu)
[![License MIT](https://custom-icon-badges.herokuapp.com/github/license/DenverCoder1/unit-converter-albert-ext.svg?logo=repo)](https://github.com/DenverCoder1/unit-converter-albert-ext/blob/main/LICENSE)
[![code style black](https://custom-icon-badges.herokuapp.com/badge/code%20style-black-black.svg?logo=black-b&logoColor=white)](https://github.com/psf/black)

Extension for converting units of length, mass, speed, temperature, time, current, luminosity, printing measurements, molecular substance, in [Albert launcher](https://albertlauncher.github.io/)

![demo](https://user-images.githubusercontent.com/20955511/147166860-2550fe42-ba6f-4ae6-a305-5e5ed26b606b.gif)

## Installation

1. Locate the `modules` directory in the Python extension data directory.

The data directories reside in the data directories of the application defined by Qt. Hence on Linux the modules would be looked up in the following directories (in this order):

```
~/.local/share/albert/org.albert.extension.python/modules
/usr/local/share/albert/org.albert.extension.python/modules
/usr/share/albert/org.albert.extension.python/modules
```

(Note: Double-clicking on a module in the settings will open the directory in the file manager.)

2. Clone this repository into your `modules` directory.

```bash
cd /path/to/modules

git clone https://github.com/DenverCoder1/unit-converter-albert-ext.git
```

3. Ensure that `pint` and `inflect` are installed using pip.

```bash
python3 -m pip install -U pint

python3 -m pip install -U inflect
```

4. Enable the extension in the settings under `Extensions > Python`.

![settings](https://user-images.githubusercontent.com/20955511/147167375-85d2bf2a-cd2b-4635-9c66-1d55dbe24d91.png)

## Usage

Type an amount and unit, followed by the word "to" or "in" and then the unit you want to convert to.

`<from_amount> <from_unit> {to|in} <to_unit>`

Examples:

`180 minutes to hrs`

`100 km in miles`

`88 mph in kph`

`32 degrees F to C`

`3.14159 rad to degrees`

## Configuration

In `config.jsonc` there are options to customize the extension:

### Aliases

To add an alias for a unit, add a key-value pair to the `aliases` object.

Example: `"sec": "second"` allows you to type `sec` instead of `second`.

Many aliases are already supported.

### Display Names

If the display name of a unit seems strange, you can override it by adding a key-value pair to the `display_names` object.

Example: `"degree_Celsiuses": "°C"` will make the displayed result appear as `32 °C` instead of `32 degree_Celsiuses`.

## Contributing

If you have any questions, suggestions, or issues, please feel free to open an issue or pull request.

## Support

💙 If you like this project, give it a ⭐ and share it with friends!

<p align="left">
  <a href="https://www.youtube.com/channel/UCipSxT7a3rn81vGLw9lqRkg?sub_confirmation=1"><img alt="Youtube" title="Youtube" src="https://custom-icon-badges.herokuapp.com/badge/-Subscribe-red?style=for-the-badge&logo=video&logoColor=white"/></a>
  <a href="https://github.com/sponsors/DenverCoder1"><img alt="Sponsor with Github" title="Sponsor with Github" src="https://custom-icon-badges.herokuapp.com/badge/-Sponsor-ea4aaa?style=for-the-badge&logo=heart&logoColor=white"/></a>
</p>

[☕ Buy me a coffee](https://ko-fi.com/jlawrence)