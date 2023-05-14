import asyncio

from mango.core.container import Container

import src.config as cfg
from src.mas.aggregator import AggregatorAgent


async def scenario():
    c = await Container.factory(addr=('127.0.0.3', 5555))
    all_aggregators = []

    small_aggregators = []
    for config in cfg.SMALL_AGGREGATORS:
        aggregator = AggregatorAgent(container=c, unit_config=config)
        await aggregator.instantiate_units()
        small_aggregators.append(aggregator)
        all_aggregators.append(aggregator)

        # to limit flexibility from aggregator
        if cfg.LIMIT_FLEXIBILITY:
            limited_flex = await aggregator.limit_flexibility(cfg.LIMIT_FLEXIBILITY)
            print(f'Flexibility limited: {limited_flex}')

        print(aggregator.gate_keeper_generation(start_date=cfg.FLEXIBILITY_START_DATE,
                                                simulation_date=cfg.SIMULATION_DATE, minimum_volume=100))
        print(aggregator.utility_function_generation(simulation_date=cfg.FLEXIBILITY_START_DATE,
                                                     start_date=cfg.SIMULATION_DATE, minimum_volume=100))
        aggregator.store_data()

    medium_aggregators = []
    for config in cfg.MEDIUM_AGGREGATORS:
        aggregator = AggregatorAgent(container=c, unit_config=config)
        await aggregator.instantiate_units()
        medium_aggregators.append(aggregator)
        all_aggregators.append(aggregator)

        # to limit flexibility from aggregator
        if cfg.LIMIT_FLEXIBILITY:
            limited_flex = await aggregator.limit_flexibility(cfg.LIMIT_FLEXIBILITY)
            print(f'Flexibility limited: {limited_flex}')

        print(aggregator.gate_keeper_generation(start_date=cfg.FLEXIBILITY_START_DATE,
                                                simulation_date=cfg.SIMULATION_DATE, minimum_volume=100))
        print(aggregator.utility_function_generation(simulation_date=cfg.FLEXIBILITY_START_DATE,
                                                     start_date=cfg.SIMULATION_DATE, minimum_volume=100))
        aggregator.store_data()

    large_aggregators = []
    for config in cfg.LARGE_AGGREGATORS:
        aggregator = AggregatorAgent(container=c, unit_config=config)
        await aggregator.instantiate_units()
        large_aggregators.append(aggregator)
        all_aggregators.append(aggregator)

        # to limit flexibility from aggregator
        if cfg.LIMIT_FLEXIBILITY:
            limited_flex = await aggregator.limit_flexibility(cfg.LIMIT_FLEXIBILITY)
            print(f'Flexibility limited: {limited_flex}')

        print(aggregator.gate_keeper_generation(start_date=cfg.FLEXIBILITY_START_DATE,
                                                simulation_date=cfg.SIMULATION_DATE, minimum_volume=100))
        print(aggregator.utility_function_generation(simulation_date=cfg.FLEXIBILITY_START_DATE,
                                                     start_date=cfg.SIMULATION_DATE, minimum_volume=100))
        aggregator.store_data()

    # shutdown agent and container
    await c.shutdown()
    for aggr in all_aggregators:
        await aggr.shutdown()
    print('Shutdown complete.')


asyncio.get_event_loop().run_until_complete(scenario())
