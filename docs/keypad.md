# Keypad

This document provides an overview of the key94187 keypads that come with no electronics. The layout of the backplate can be found in `docs/key94187.jpg`.

## Naming Conventions

We shall refer to the various connectors and pins in the following fashion, with the origin is the top left when looking from the back, with the header on the bottom.:

- Large connectors that come in top/bottom pairs shall be referred to by their labe + "top" and "bottom", so for instance the Hook connectors shall be Hook Top and Hook Bottom
- Pins in the ribbon cable connector shall be referred to as "Ribbon[<row>,<col>]", so for instance the pin on the first row third column will be Ribbon[1,3].
- Pins on the bottom labeled J2 will be numbered left to right from 1 to 7, and referred to as "J2[<pin number>]", so for instance the third pin will be "J2[3]"

## Backplate Connectivity

The connectors and pins on the backplate are connected to the ribbon cable connector as follows:

```
Ribbon[1,1] = +5V
Ribbon[1,2] = J2[5]
Ribbon[1,3] = J2[3]
Ribbon[1,4] = J2[6], FUNCT. A BOT
Ribbon[1,5] = J2[2], FUNCT. C BOT
Ribbon[1,6] = GND, HOOK TOP, VOL TOP
Ribbon[1,7] = VOL BOT
Ribbon[1,8] = RINGER
Ribbon[1,9] = EAR TOP
Ribbon[1,10] = MIC TOP
Ribbon[2,1] = floating?
Ribbon[2,2] = J2[4], FUNCT. D BOT
Ribbon[2,3] = J2[7]
Ribbon[2,4] = FUNCT. A TOP, FUNCT. B TOP, FUNCT. C TOP, FUNCT. D TOP
Ribbon[2,5] = J2[1], FUNCT. B BOT
Ribbon[2,6] = GND, HOOK TOP, VOL TOP
Ribbon[2,7] = HOOK BOT
Ribbon[2,8] = +12V
Ribbon[2,9] = EAR BOT
Ribbon[2,10] = MIC BOT
```

From the J2 direction, we have

```
J2[1] = Ribbon[2,5], FUNCT. B BOT
J2[2] = Ribbon[1,5], FUNCT. C BOT
J2[3] = Ribbon[1,3]
J2[4] = Ribbon[2,2], FUNCT. D BOT
J2[5] = Ribbon[1,2]
J2[6] = Ribbon[1,4], FUNCT. A BOT
J2[7] = Ribbon[2,3]
```

## Keypad Connectivity

The keypad is connected to the J2 pins as well. There are 7 J2 pins total, 4 of which are connected to FUNCT. A-D BOT. These correspond to the 4 rows of the keypad. FUNCT. A-D are the 4 non-present function keys that some phones have, and which this keypad has connectors for. The remaining three pins correspond to the columns of the keypad. The function key column is not present on the J2 connector, but is present in the ribbon connector as the FUNCT. A-D TOP pin, i.e. Ribbon[2,4].

When a key is pressed, the pin for the row is connected to a pin for the column. The connectivity of the rows and columns is given as follows:

```
Row[1] = J2[6] = Ribbon[1,4]
Row[2] = J2[1] = Ribbon[2,5]
Row[3] = J2[2] = Ribbon[1,5]
Row[4] = J2[4] = Ribbon[2,2]
Col[1] = J2[5] = Ribbon[1,2]
Col[2] = J2[7] = Ribbon[2,3]
Col[3] = J2[3] = Ribbon[1,3]
```
