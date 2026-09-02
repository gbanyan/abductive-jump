from abductive_jump.hypothesis_genome import (
    HypothesisGenome,
    crossover_values,
    exchange_attributes,
    mutate_value,
)


def test_hypothesis_genome_value_mutation_crossover_and_exchange_are_provenanced():
    left = HypothesisGenome((1.0, 2.0, 3.0), (0, 1))
    right = HypothesisGenome((4.0, 5.0, 6.0), (1, 0))
    mutated, mutation = mutate_value(left, 1, 0.5, 10)
    crossed, crossover = crossover_values(left, right, 1, 11)
    exchanged, exchange = exchange_attributes(left, 0, 2, 12)
    assert mutated.values == (1.0, 2.5, 3.0)
    assert crossed.values == (1.0, 5.0, 6.0)
    assert exchanged.values == (3.0, 2.0, 1.0)
    assert mutation.parent_hashes == (left.genome_hash,)
    assert crossover.parent_hashes == (left.genome_hash, right.genome_hash)
    assert exchange.child_hash == exchanged.genome_hash
