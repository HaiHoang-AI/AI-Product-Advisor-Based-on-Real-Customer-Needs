"""Test follow-up engine with representative customer scenarios from the brief."""
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.core.follow_up_engine import get_follow_up_questions
from backend.models.schemas import Category, CustomerNeed


class TestScenarios(unittest.TestCase):

    def test_refrigerator_missing_household_size(self):
        need = CustomerNeed(
            category=Category.TU_LANH,
            budget_max=15000000,
            priorities=["tiết kiệm điện"],
        )
        questions = get_follow_up_questions(need)
        self.assertTrue(any("bao nhiêu người" in q["question"] for q in questions))

    def test_air_conditioner_missing_room_area(self):
        need = CustomerNeed(
            category=Category.MAY_LANH,
            budget_max=20000000,
            priorities=["ít ồn"],
        )
        questions = get_follow_up_questions(need)
        self.assertTrue(any("bao nhiêu m²" in q["question"] for q in questions))

    def test_complete_need_no_questions(self):
        need = CustomerNeed(
            category=Category.TU_LANH,
            budget_max=12000000,
            household_size=4,
            priorities=["tiết kiệm điện"],
            additional_notes="thích kiểu ngăn đá dưới",
            installment=False,
        )
        # When all key factors are provided, few or no questions returned
        questions = get_follow_up_questions(need)
        self.assertFalse(any("bao nhiêu người" in q["question"] for q in questions))


if __name__ == "__main__":
    unittest.main()
