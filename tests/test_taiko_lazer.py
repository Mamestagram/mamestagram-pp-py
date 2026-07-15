from pathlib import Path
from unittest import TestCase

from mames_pp_py import Beatmap, Difficulty, GameMode, Performance


MAP_PATH = Path(__file__).parent / "resources" / "diffcalc-test.osu"
EPSILON = 1e-12

LAZER_CASES = (
    {
        "name": "NM",
        "mods": 0,
        "stars": 1.7152719633248064,
        "rhythm": 0.05015488453386578,
        "reading": 2.116519282046003e-9,
        "color": 0.14397995960696108,
        "stamina": 1.5211371170674601,
        "mechanical_difficulty": 1.6651170766744212,
        "mono_stamina_factor": 0.8082384132909826,
        "stamina_top_strains": 28.69138730242241,
        "consistency_factor": 0.4447501432652793,
        "great_hit_window": 28.5,
        "ok_hit_window": 67.5,
        "pp": 106.0734255680183,
        "pp_difficulty": 5.192487945534822,
        "pp_accuracy": 100.88093762248347,
        "estimated_unstable_rate": 141.6908765618353,
        "gradual_final_stars": 1.7152704896781434,
    },
    {
        "name": "DT",
        "mods": 64,
        "stars": 2.220969499173367,
        "rhythm": 0.07094112336504874,
        "reading": 7.97093746211745e-6,
        "color": 0.14799332005740454,
        "stamina": 2.002027084813451,
        "mechanical_difficulty": 2.1500204048708556,
        "mono_stamina_factor": 0.8491265933219949,
        "stamina_top_strains": 33.18108215154794,
        "consistency_factor": 0.45313750560101457,
        "great_hit_window": 19.0,
        "ok_hit_window": 45.0,
        "pp": 188.7334974302947,
        "pp_difficulty": 13.91995095690722,
        "pp_accuracy": 174.81354647338748,
        "estimated_unstable_rate": 94.46058437455687,
        "gradual_final_stars": 2.220919705963918,
    },
    {
        "name": "HR",
        "mods": 16,
        "stars": 1.7152756639610034,
        "rhythm": 0.050090703458360364,
        "reading": 0.0021986634935717256,
        "color": 0.14379571456230564,
        "stamina": 1.5191905824467657,
        "mechanical_difficulty": 1.6629862970090714,
        "mono_stamina_factor": 0.8082384132909826,
        "stamina_top_strains": 28.69138730242241,
        "consistency_factor": 0.44475016923502625,
        "great_hit_window": 19.5,
        "ok_hit_window": 50.5,
        "pp": 175.65865173973523,
        "pp_difficulty": 6.20984791982135,
        "pp_accuracy": 169.44880381991388,
        "estimated_unstable_rate": 96.94638922651889,
        "gradual_final_stars": 1.7152741903049118,
    },
)


class TaikoLazerBindingTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.map = Beatmap(path=str(MAP_PATH))
        cls.map.convert(GameMode.Taiko, None)

    def assertClose(self, actual: float, expected: float) -> None:
        self.assertAlmostEqual(actual, expected, delta=EPSILON)

    def test_converted_taiko_difficulty_matches_lazer_reference(self) -> None:
        for case in LAZER_CASES:
            with self.subTest(mods=case["name"]):
                attrs = Difficulty(mods=case["mods"], lazer=True).calculate(self.map)

                self.assertEqual(attrs.mode, GameMode.Taiko)
                self.assertTrue(attrs.is_convert)
                self.assertEqual(attrs.max_combo, 117)

                for field in (
                    "stars",
                    "rhythm",
                    "reading",
                    "color",
                    "stamina",
                    "mechanical_difficulty",
                    "mono_stamina_factor",
                    "stamina_top_strains",
                    "consistency_factor",
                    "great_hit_window",
                    "ok_hit_window",
                ):
                    self.assertClose(getattr(attrs, field), case[field])

    def test_taiko_performance_reusing_attributes_matches_lazer(self) -> None:
        for case in LAZER_CASES:
            with self.subTest(mods=case["name"]):
                attrs = Difficulty(mods=case["mods"], lazer=True).calculate(self.map)
                kwargs = {
                    "mods": case["mods"],
                    "lazer": True,
                    "combo": attrs.max_combo,
                    "n300": attrs.max_combo,
                }

                from_attrs = Performance(**kwargs).calculate(attrs)
                from_map = Performance(**kwargs).calculate(self.map)

                for performance in (from_attrs, from_map):
                    self.assertClose(performance.pp, case["pp"])
                    self.assertClose(
                        performance.pp_difficulty,
                        case["pp_difficulty"],
                    )
                    self.assertClose(performance.pp_accuracy, case["pp_accuracy"])
                    self.assertClose(
                        performance.estimated_unstable_rate,
                        case["estimated_unstable_rate"],
                    )

    def test_taiko_gradual_matches_lazer_at_last_scoring_hit(self) -> None:
        for case in LAZER_CASES:
            with self.subTest(mods=case["name"]):
                difficulty = Difficulty(mods=case["mods"], lazer=True)
                regular = difficulty.calculate(self.map)
                gradual = list(difficulty.gradual_difficulty(self.map))

                self.assertEqual(len(gradual), regular.max_combo)

                last = gradual[-1]
                self.assertEqual(last.max_combo, regular.max_combo)
                # The map ends in a non-scoring spinner, so lazer's timed value
                # at the last scoring hit intentionally differs from full-map difficulty.
                self.assertClose(last.stars, case["gradual_final_stars"])
