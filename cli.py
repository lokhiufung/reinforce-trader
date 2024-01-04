import click
from importlib import import_module
from datetime import datetime, timedelta

from reinforce_trader.research.datalake_client import DatalakeClient


DL_CLIENT = DatalakeClient(datalake_dir='./data')
# Setting the date range (last month)
DEFAULT_END_DATE = datetime.today()


@click.group()
def cli():
    """
    CLI application to manage data.

    This application provides a set of commands for data management. You can perform
    operations like adding and updating data sources. For help on specific commands, 
    run them with the '-h' or '--help' flag.
    """
    pass


@cli.group()
def datalake():
    """
    Datalake operations group.

    This group includes commands related to Datalake operations. You can add new data sources
    or update existing ones. For specific operations, use 'add' or 'update' commands 
    with this group. For more information on these commands, use '-h' or '--help'.
    """
    pass


@datalake.command()
@click.option('--name', required=True, help='The name of the data source to update')
@click.option('--start-date', required=False, default=None, help='The starting date of new data. Default to be the date of trailling half year from the ending date')
@click.option('--end-date', required=False, default=None, help='The ending date of the new data. Defualt to be today')
def update(name, start_date, end_date):
    """
    Update an existing data source.

    This command allows you to update an existing data source specified by its name.
    """
    data_source = import_module(f'reinforce_trader.research.data_sources.{name}_data_source')
    if end_date is None:
        end_date = datetime.today()
    if start_date is None:
        # use trailling half year as the default start_date
        start_date = end_date - timedelta(days=30*6)
    data_source.update_data(DL_CLIENT, start_date, end_date)


@datalake.command()
@click.option('--name', required=True, help='The name of the data source to add')
@click.option('--start-date', required=False, default=None, help='The starting date of new data. Default to be the date of trailling half year from the ending date')
@click.option('--end-date', required=False, default=None, help='The ending date of the new data. Defualt to be today')
def add(name, start_date, end_date):
    """
    Add a new data source.

    This command allows you to add a new data source with a specified name.
    """
    data_source = import_module(f'reinforce_trader.research.data_sources.{name}_data_source')
    if end_date is None:
        end_date = datetime.today()
    if start_date is None:
        # use trailling 10 year as the default start_date
        start_date = end_date - timedelta(days=10*365)
    data_source.add_data(DL_CLIENT, start_date, end_date)



if __name__ == '__main__':
    cli()
