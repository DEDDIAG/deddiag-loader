import click
import os


@click.group()
def cli():
    pass


@cli.command()
@click.option("--host", required=True, default=lambda: os.environ.get('DEDDIAG_DB_HOST', 'localhost'))
@click.option("--db", required=True, default=lambda: os.environ.get('DEDDIAG_DB_NAME', 'postgres'))
@click.option("--port", required=True, default=lambda: os.environ.get('DEDDIAG_DB_PORT', '5432'))
@click.option("--username", required=True, default=lambda: os.environ.get('DEDDIAG_DB_USER', 'postgres'))
@click.option("--password", hide_input=True, default=lambda: os.environ.get('DEDDIAG_DB_PW'), show_default='')
@click.option("--item-id", required=True)
@click.option("--label-id", default=None)
@click.option("--start-date", type=click.DateTime(), default=None)
@click.option("--stop-date", type=click.DateTime(), default=None)
@click.argument("file_name", required=True)
def save(host, db, user, port, password, item_id, label_id, start_date, stop_date, file_name):
    """Export data to numpy array"""
    from . import Connection, MeasurementsExpandedWithLabels
    import numpy as np

    con = Connection(host, port, db, user, password)
    measurements = MeasurementsExpandedWithLabels(item_id, label_id, start_date, stop_date).request(con)
    np.save("{}_measurement_with_labels.npy".format(file_name), np.array(measurements))


@cli.command()
@click.option("--host", required=True, default=lambda: os.environ.get('DEDDIAG_DB_HOST', 'localhost'))
@click.option("--db", required=True, default=lambda: os.environ.get('DEDDIAG_DB_NAME', 'postgres'))
@click.option("--port", required=True, default=lambda: os.environ.get('DEDDIAG_DB_PORT', '5432'))
@click.option("--username", required=True, default=lambda: os.environ.get('DEDDIAG_DB_USER', 'postgres'))
@click.option("--password", hide_input=True, default=lambda: os.environ.get('DEDDIAG_DB_PW'), show_default='')
def stats(host, db, user, port, password):
    """Print dataset stats"""
    from . import Connection, Houses, Items, MeasurementsRange, Annotations
    con = Connection(host, port, db, user, password)
    items = Items().request(con)
    row_format = "{:>4}\t{:>30}\t{:>20}\t{:>20}\t{:>5}"
    print(row_format.format("Id", "Name", "first date", "last date", "num annotations"))

    for _, house in Houses().request(con).iterrows():
        print("-"*42 + f" House {house.id:2} " + "-"*42)
        for _, item in items.loc[items.house == house.id].iterrows():
            m_range = MeasurementsRange(item['id']).request(con)
            annotations = Annotations(item_id=item['id']).request(con)
            print(row_format.format(item['id'],
                                    item['name'][:30],
                                    str(m_range.min_date.item()),
                                    str(m_range.max_date.item()),
                                    len(annotations)))
