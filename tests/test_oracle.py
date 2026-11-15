import unittest

from oracle import wot_score


class WebOfTrustScoreTests(unittest.TestCase):
    def test_score_counts_seed_accounts_that_follow_the_candidate(self):
        seed_a = "a" * 64
        seed_b = "b" * 64
        seed_c = "c" * 64
        candidate = "d" * 64
        another = "e" * 64

        follows_map = {
            seed_a: {candidate, another},
            seed_b: {candidate},
            seed_c: {another},
        }

        self.assertAlmostEqual(wot_score(candidate, {seed_a, seed_b, seed_c}, follows_map), 2 / 3)
        self.assertAlmostEqual(wot_score(another, {seed_a, seed_b, seed_c}, follows_map), 2 / 3)

    def test_candidate_following_seed_accounts_does_not_increase_its_score(self):
        seed_a = "a" * 64
        seed_b = "b" * 64
        candidate = "d" * 64

        follows_map = {
            seed_a: {candidate},
            seed_b: set(),
            candidate: {seed_a, seed_b},
        }

        self.assertEqual(wot_score(candidate, {seed_a, seed_b}, follows_map), 0.5)

    def test_candidate_scores_are_sorted_highest_first_with_stable_ties(self):
        from oracle import score_candidates

        seed_a = "a" * 64
        seed_b = "b" * 64
        candidate_a = "c" * 64
        candidate_b = "d" * 64

        scored = score_candidates(
            {seed_a, seed_b},
            {
                seed_a: {candidate_a, candidate_b},
                seed_b: {candidate_a},
            },
        )

        self.assertEqual(list(scored.items()), [
            (candidate_a, 1.0),
            (candidate_b, 0.5),
        ])

    def test_empty_seed_set_returns_zero(self):
        self.assertEqual(wot_score("d" * 64, set(), {}), 0)


if __name__ == "__main__":
    unittest.main()
