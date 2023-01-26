> **Archive Notice**
> 
> This repo is no longer needed since this extension is now merged into the [upstream Python plugin repo](https://github.com/albertlauncher/python/tree/master/unit_converter).

# unit-converter-albert-ext

[![discord](https://custom-icon-badges.herokuapp.com/discord/819650821314052106?color=5865F2&logo=discord-outline&logoColor=white "Dev Pro Tips Discussion & Support Server")](https://discord.gg/fPrdqh3Zfu)
[![License MIT](https://custom-icon-badges.herokuapp.com/github/license/DenverCoder1/unit-converter-albert-ext.svg?logo=repo)](https://github.com/DenverCoder1/unit-converter-albert-ext/blob/main/LICENSE)
[![code style black](https://custom-icon-badges.herokuapp.com/badge/code%20style-black-black.svg?logo=black-b&logoColor=white)](https://github.com/psf/black)

Extension for converting units of length, mass, speed, temperature, time, current, luminosity, printing measurements, molecular substance, currency, and more in [Albert launcher](https://albertlauncher.github.io/)

![demo 0.18](https://user-images.githubusercontent.com/20955511/211650412-b42412f3-c4d5-4d2a-8b77-05ff39fcb48e.gif)

## Installation

1. Locate the `plugins` directory in the Python extension data directory.

The data directories reside in the data directories of the application defined by Qt. Hence on Linux the modules would be looked up in the following directories (in this order):

```
~/.local/share/albert/python/plugins
/usr/local/share/albert/python/plugins
/usr/share/albert/python/plugins
```

2. Clone this repository into your `plugins` directory.

```bash
cd /path/to/plugins  # see above for the path

git clone https://github.com/DenverCoder1/unit-converter-albert-ext.git
```

3. Ensure that `pint` and `inflect` are installed in `~/.local/share/albert/python/site-packages`.

```bash
cd unit-converter-albert-ext

pip install -U -r requirements.txt -t ~/.local/share/albert/python/site-packages
```

4. Enable the extension in the settings under the `Plugins` tab.

![open settings](https://user-images.githubusercontent.com/20955511/211635567-f732b0cb-da8f-403f-83e1-59c7d0b137f1.png)

![enable plugin](https://user-images.githubusercontent.com/20955511/211635868-a817c6a9-2bcb-43f7-858f-731a9d51685b.png)

## Usage

Type the trigger, followed by the amount and unit, the word "to" or "in", and then the unit you want to convert to.

`<trigger> <amount> <from_unit> {to|in} <to_unit>`

Examples:

`convert 180 minutes to hrs`

`convert 100 km to miles`

`convert 88 mph to kph`

`convert 32 degrees F to C`

`convert 3.14159 rad to degrees`

`convert 100 EUR to USD`

To configure the trigger to be something other than "convert ", open the `Triggers` tab in the Albert settings.

![configure trigger](https://user-images.githubusercontent.com/20955511/211632106-981ce5a8-0311-47d5-aefe-3ab9d669fc3f.png)

## Configuration

In `config.jsonc` there are options to customize the behavior of the extension:

### Rounding Precision

The `rounding_precision` option controls how many decimal places the result will be rounded to. By default, this is 3.

The `rounding_precision_zero` option controls how many decimal places the result will be rounded to when the result is close to zero. By default, this is 12.

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
