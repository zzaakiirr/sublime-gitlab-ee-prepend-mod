# About

Plugin for Sublime Text 3 that creates/opens EE module that is prepended to original class in app folder. And vice a versa if EE module is opened

# Features

1. Adds line `<KlassName>.prepend_mod` to original file
2. Creates or opens prepended module in ee folder
3. If file in ee folder is opened then original file will be opened (to which EE module is prepended)


# Installation

**Required steps**:

1. Open Sublime Text
2. Goto Tools -> Developer -> New plugin
3. Create new file - EePrependMod.py
4. Copy-paste file with same name from this repository

**Optional steps (shortcut creation)**

1. Goto Sublime Text -> Preferences -> Key Bindings
2. Add key binding for plugin:
```
{
    "keys": ["super+shift+v"], // Example, you can set your own keys
    "command": "ee_prepend_mod"
}
```

**Demo**
TODO
