# AllConfig

This is a simple Klipper utility that allows for outputting your entire config, as Klipper sees it, to a file.

This is the same config that is shown at the top of your `klippy.log`, but is easier to access since:

1. It's in your config folder, so you don't have to navigate to the logs section
2. It's a lot smaller than your log, so it's a lot quicker to open and scroll through, CTRL+F, etc.

## Installation

In SSH:

```
cd ~/
git clone https://github.com/3DCoded/Klipper-AllConfig
cd ~/Klipper-AllConfig
ln -f allconfig.py ~/klipper/klippy/extras/allconfig.py
sudo service klipper restart
```

## Configuration

Anywhere in your `printer.cfg`, add:

```
[allconfig]
# Optionally, define a custom output path.
# output: ~/printer_data/config/allconfig.cfg
```

Restart Klipper.

## Usage

Whenever you restart Klipper, you will now see an `allconfig.cfg` file in the same folder as your `printer.cfg`. If you defined a custom `output`, it will be at the path you selected.

Inside will be the entirety of your Klipper config, as seen by Klipper. This means that all `include` sections, overridden sections, and SAVE_CONFIG are all taken into account. This can help to diagnose common config issues.

## Updating

In SSH:

```
cd ~/Klipper-AllConfig
git pull
ln -f allconfig.py ~/klipper/klippy/extras/allconfig.py
sudo service klipper restart
```

## Other Projects

If you liked this project, don't forget to give it a star! Also check out my other projects:

- [3MS](https://3ms.3dcoded.xyz/) modular multi-material system for Klipper
- [DynamicMacros](https://dynamicmacros.3dcoded.xyz/) never restart Klipper for simple macros...and much more
- [KlipperMaintenance](https://www.3dcoded.xyz/KlipperMaintenance/) Keep your 3D printer running smoothly