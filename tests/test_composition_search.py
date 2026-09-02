from abductive_jump.composition_search import depth_one_search, random_search, structured_search
from abductive_jump.worlds import generate_world


def test_search_budgets_and_determinism():
    public = generate_world("state_invention", 31).public()
    first = structured_search(public, 99, breadth=48, max_depth=4)
    again = structured_search(public, 99, breadth=48, max_depth=4)
    assert first == again
    assert first.primitive_operations <= 192
    assert len(first.selected) == 3
    assert max(item.candidate.depth for item in first.evaluated) == 4

    atomic = depth_one_search(public, 99, operation_budget=192)
    assert atomic.primitive_operations == 192
    assert all(item.candidate.depth == 1 for item in atomic.evaluated)

    random = random_search(public, 99, breadth=48, max_depth=4)
    assert random.primitive_operations == 192
    assert len(random.evaluated) == 192
