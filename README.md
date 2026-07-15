# mames-pp-py

Library to calculate difficulty and performance attributes for all [osu!] modes.

This is a Python binding to the [Rust] library [mames-pp] which was bootstrapped through [PyO3].
As such, its performance is much faster than a native python library.

## Usage

The library exposes multiple classes. See [`mames_pp_py.pyi`](./mames_pp_py.pyi) for the complete typed API.

- `Beatmap`: Parsed `.osu` file
- `GameMode`
- Calculators
  - `Difficulty`: Calculates difficulty attributes, strains, or gradual calculators
  - `Performance`: Calculates performance attributes
  - `GradualDifficulty`: Calculates difficulty attributes after each hit object
  - `GradualPerformance`: Calculates performance attributes after each hit result
  - `BeatmapAttributesBuilder`: Calculates beatmap attributes
- Results
  - `DifficultyAttributes`
  - `Strains`: Strain values suitable for plotting difficulty over time
  - `PerformanceAttributes`
  - `BeatmapAttributes`
- `HitResultPriority`: Controls how generated hit results realize specified accuracy
- `ScoreState`: Hit results and max combo passed to gradual calculators

## Example

### Calculating performance

```py
import mames_pp_py as mames

# either `path`, `bytes`, or `content` must be specified when parsing a map
map = mames.Beatmap(path = "/path/to/file.osu")

# Optionally convert to a specific mode for optionally given mods
map.convert(mames.GameMode.Mania, "6K")

perf = mames.Performance(
    # various kwargs available
    accuracy = 98.76,
    misses = 2,
    combo = 700,
    hitresult_priority = mames.HitResultPriority.WorstCase, # favors bad hitresults
)

# Each kwarg can also be specified afterwards through setters
perf.set_accuracy(99.11) # override previously specified accuracy
perf.set_mods(8 + 64)    # HDDT
perf.set_clock_rate(1.4)

# Second argument of map attributes specifies whether mods still need to be accounted for
# `True`: mods already considered; `False`: value should still be adjusted
perf.set_ar(10.5, True)
perf.set_od(5, False)

# Calculate for the map
attrs = perf.calculate(map)

# Note that calculating via map will have to calculate difficulty attributes
# internally which is fairly expensive. To speed it up, you can also pass in
# previously calculated attributes, but be sure they were calculated for the
# same difficulty settings like mods, clock rate, custom map attributes, ...

perf.set_accuracy(100)
perf.set_misses(None)
perf.set_combo(None)

# Calculate a new set of attributes by re-using previous attributes instead of the map
max_attrs = perf.calculate(attrs)

print(f'PP: {attrs.pp}/{max_attrs.pp} | Stars: {max_attrs.difficulty.stars}')
```

### Gradual calculation

```py
import mames_pp_py as mames

# Parsing the map, this time through the `content` kwarg
with open("/path/to/file.osu") as file:
    map = mames.Beatmap(content = file.read())

# Specifying some difficulty parameters
diff = mames.Difficulty(
    mods = 16 + 1024, # HRFL
    clock_rate = 1.1,
    ar = 10.2,
    ar_with_mods = True,
)

# Gradually calculating *difficulty* attributes
gradual_diff = diff.gradual_difficulty(map)

for i, attrs in enumerate(gradual_diff, 1):
    print(f'Stars after {i} hitobjects: {attrs.stars}')

# Gradually calculating *performance* attributes
gradual_perf = diff.gradual_performance(map)
i = 1

while True:
    state = mames.ScoreState(
        max_combo = i,
        n300 = i,
        n100 = 0,
        # ...
    )

    attrs = gradual_perf.next(state)

    if attrs is None:
        # All hitobjects have been processed
        break

    print(f'PP: {attrs.pp}')
    i += 1
```

## Mods

Wherever mods are specified, their type should coincide with the following alias definition:
```py
GameMods = Union[int, str, GameMod, List[Union[GameMod, str, int]]]
GameMod = dict[str, Union[str, GameModSettings]]
GameModSettings = dict[str, Union[bool, float, str]]
```

That means, mods can be given either through their [(legacy) bitflags](https://github.com/ppy/osu-api/wiki#reference),
a string for acronyms, a "GameMod" `dict`, or a sequence whose items are either
a "GameMod" `dict`, a single acronym string, or bitflags for a single mod.

A "GameMod" `dict` **must** have the item `'acronym': str` and an optional item `'settings': GameModSettings`.

Some examples for valid mods look as follows:

```py
mods = 8 + 64              # Hidden, DoubleTime
mods = "hRNcWIez"          # HardRock, Nightcore, Wiggle, Easy
mods = { 'acronym': "FI" } # FadeIn
mods = [
    1024,
    'nf',
    {
        'acronym': "AC",
        'settings': {
            'minimum_accuracy': 95,
            'restart': True
        }
    }
] # Flashlight, NoFail, AccuracyChallenge

import json
mods_json = '[{"acronym": "TC"}, {"acronym": "HT", "settings": {"speed_change": 0.6}}]'
mods = json.loads(mods_json) # Traceable, HalfTime
```

## Installing mames-pp-py

Installing mames-pp-py requires Python 3.8 or newer and a [supported version of Rust](https://github.com/PyO3/PyO3#usage).
CPython 3.14 is supported.

Once [Python] and [Rust](https://www.rust-lang.org/learn/get-started) are ready to go, install directly from this repository:

```sh
$ pip install git+https://github.com/Mamestagram/mamestagram-pp-py
```

## Learn More
- [mames-pp]
- [Rust]
- [PyO3]

[osu!]: https://osu.ppy.sh/home
[Rust]: https://www.rust-lang.org
[mames-pp]: https://github.com/Mamestagram/mamestagram-pp-rs
[PyO3]: https://github.com/PyO3/pyo3
[Python]: https://www.python.org/downloads/
