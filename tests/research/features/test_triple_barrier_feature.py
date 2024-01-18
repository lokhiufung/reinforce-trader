import pytest
import numpy as np
from reinforce_trader.research.features.triple_barrier_feature import TripleBarrierFeature


# Fixture for creating TripleBarrierFeature instance
@pytest.fixture
def triple_barrier_feature():
    r_stop = 0.02  # Example value, adjust as needed
    r_take = 0.03  # Example value, adjust as needed
    return TripleBarrierFeature(r_stop, r_take)


# Now use this fixture in your tests
def test_take_profit(triple_barrier_feature):
    ohlc_sequence = np.array([[
        [100, 102,  100, 101],  # Day 1: Does not hit take profit
        [101, 103.5, 100, 102], # Day 2: Hits take profit (High = 103.5)
        [102, 104, 101, 103],  # Day 3: Price after take profit is hit
        # ... (add more days if needed)
    ]])
    result = triple_barrier_feature._run(ohlc_sequence)
    assert result[0][0] == 1  # Check if label is 1 (take profit)


def test_stop_loss(triple_barrier_feature):
    ohlc_sequence = np.array([[
        [100, 102, 99, 101],  # Day 1: Does not hit stop loss
        [101, 102, 97.5, 98], # Day 2: Hits stop loss (Low = 97.5)
        [98, 99, 95, 96],    # Day 3: Price after stop loss is hit
        # ... (add more days if needed)
    ]])
    result = triple_barrier_feature._run(ohlc_sequence)
    assert result[0][0] == -1  # Check if label is -1 (stop loss)


def test_neither(triple_barrier_feature):
    ohlc_sequence = np.array([[
        [100, 102.5, 99, 101],  # Day 1: Does not hit either threshold
        [101, 102.8, 99.2, 102],# Day 2: Still within thresholds
        [102, 102.9, 99.5, 102.5], # Day 3: Continues to be within thresholds
        # ... (more days can be added, none should breach the stop loss or take profit levels)
    ]])
    result = triple_barrier_feature._run(ohlc_sequence)
    assert result[0][0] == 0  # Check if label is 0 (neither)

