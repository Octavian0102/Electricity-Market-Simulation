import pytest as pytest
from mango.core.container import Container

from src.mas.aggregator import AggregatorAgent


@pytest.mark.asyncio
async def test_limitation():
    example_unit_config = {'PV': [2, 1], 'battery': [1], 'heatpump': [1], 'e-charge': [1]}
    example_limitation = 0.1

    c = await Container.factory(addr=('127.0.0.3', 5555))
    aggregator = AggregatorAgent(container=c, unit_config=example_unit_config)
    await aggregator.instantiate_units()
    sum_before = sum([aggregator.aggregated_load[i] + aggregator.aggregated_generation[i] for i in
                      range(len(aggregator.aggregated_load))])
    sum_after = sum(await aggregator.limit_flexibility(example_limitation))
    diff = round(sum_after / sum_before, 1)
    assert diff == 1 - example_limitation

    await c.shutdown()
    await aggregator.shutdown()
