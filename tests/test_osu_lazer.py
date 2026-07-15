from pathlib import Path
from unittest import TestCase

from mames_pp_py import Beatmap, Difficulty, Performance


MAP_PATH = Path(__file__).parent / "resources" / "diffcalc-test.osu"
EPSILON = 1e-9


class OsuLazerBindingTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.map = Beatmap(path=str(MAP_PATH))

    def assertClose(self, actual: float, expected: float) -> None:
        self.assertAlmostEqual(actual, expected, delta=EPSILON)

    def test_vanilla_osu_nm_matches_lazer_reference(self) -> None:
        difficulty = Difficulty(lazer=True).calculate(self.map)
        performance = Performance(lazer=True).calculate(difficulty)

        self.assertClose(difficulty.stars, 6.524323005451469)
        self.assertClose(difficulty.aim, 3.8093990088670195)
        self.assertClose(difficulty.speed, 1.564710574509105)
        self.assertClose(difficulty.reading, 1.7803497292117219)
        self.assertClose(
            difficulty.reading_difficult_note_count,
            32.18033420358422,
        )
        self.assertClose(difficulty.nested_score_per_object, 172.90322580645162)
        self.assertClose(difficulty.maximum_legacy_combo_score, 389_808.0)
        self.assertEqual(difficulty.max_combo, 239)

        self.assertClose(performance.pp, 291.1510007361912)
        self.assertClose(performance.pp_aim, 214.8629763621098)
        self.assertClose(performance.pp_speed, 12.604838421331243)
        self.assertClose(performance.pp_reading, 22.572307597136877)
        self.assertClose(performance.pp_accuracy, 27.715025148546076)

    def test_vanilla_osu_dt_matches_lazer_reference(self) -> None:
        difficulty = Difficulty(mods=64, lazer=True).calculate(self.map)
        performance = Performance(mods=64, lazer=True).calculate(difficulty)

        self.assertClose(difficulty.stars, 9.467769487912906)
        self.assertClose(performance.pp, 878.0491184948831)

    def test_all_supported_mod_input_shapes(self) -> None:
        expected = Difficulty(mods=8, lazer=True).calculate(self.map).stars

        for mods in ("HD", {"acronym": "HD"}, ["HD"], [8]):
            with self.subTest(mods=mods):
                actual = Difficulty(mods=mods, lazer=True).calculate(self.map).stars
                self.assertClose(actual, expected)

    def test_classic_raw_score_miss_estimation(self) -> None:
        difficulty = Difficulty(lazer=False).calculate(self.map)
        calculator = Performance(
            lazer=False,
            combo=200,
            n300=120,
            n100=2,
            n50=1,
            misses=1,
        )
        calculator.set_legacy_total_score(250_000)
        performance = calculator.calculate(difficulty)

        self.assertClose(performance.pp, 222.9124271871467)
        self.assertClose(performance.effective_miss_count, 1.4756347294773247)
        self.assertClose(
            performance.combo_based_estimated_miss_count,
            1.168399996947791,
        )
        self.assertClose(
            performance.score_based_estimated_miss_count,
            1.4756347294773247,
        )
        self.assertClose(
            performance.aim_estimated_slider_breaks,
            3.079603957617613e-5,
        )
        self.assertClose(
            performance.speed_estimated_slider_breaks,
            3.375200378321988e-5,
        )
