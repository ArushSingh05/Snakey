import unittest

from play import award_food_xp, award_kill, award_death, register_collision_outcome, resolve_collision_result


class ProgressStatsTests(unittest.TestCase):
    def test_food_xp_uses_progressive_multiplier(self):
        profile = {"food_consumed": 0, "xp": 0, "level": 1}

        for _ in range(25):
            award_food_xp(profile)
        self.assertEqual(profile["food_consumed"], 25)
        self.assertEqual(profile["xp"], 25)

        for _ in range(50):
            award_food_xp(profile)
        self.assertEqual(profile["food_consumed"], 75)
        self.assertEqual(profile["xp"], 125)

        award_food_xp(profile)
        self.assertEqual(profile["food_consumed"], 76)
        self.assertEqual(profile["xp"], 128)

    def test_kill_and_death_tracking(self):
        profile = {"kills": 0, "deaths": 0, "xp": 0, "level": 1}

        award_kill(profile)
        self.assertEqual(profile["kills"], 1)
        self.assertEqual(profile["xp"], 10)

        award_death(profile)
        self.assertEqual(profile["deaths"], 1)

    def test_collision_outcomes_update_kd_correctly(self):
        profile = {"kills": 0, "deaths": 0, "xp": 0, "level": 1}

        register_collision_outcome(profile, player_won=True)
        self.assertEqual(profile["kills"], 1)
        self.assertEqual(profile["deaths"], 0)

        register_collision_outcome(profile, player_won=False)
        self.assertEqual(profile["kills"], 1)
        self.assertEqual(profile["deaths"], 1)

    def test_collision_result_maps_player_hit_to_enemy_win(self):
        player_won, winner = resolve_collision_result(player_hit_other_snake=True)
        self.assertFalse(player_won)
        self.assertEqual(winner, "Enemy")

        player_won, winner = resolve_collision_result(player_hit_other_snake=False)
        self.assertTrue(player_won)
        self.assertEqual(winner, "Player")


if __name__ == "__main__":
    unittest.main()
