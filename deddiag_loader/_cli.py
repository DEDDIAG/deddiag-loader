import logging
from pathlib import Path

import click
import os


@click.group()
def cli():
    pass


@cli.command()
@click.option("--host", required=True, default=lambda: os.environ.get('DEDDIAG_DB_HOST', 'localhost'))
@click.option("--db", required=True, default=lambda: os.environ.get('DEDDIAG_DB_NAME', 'postgres'))
@click.option("--port", required=True, default=lambda: os.environ.get('DEDDIAG_DB_PORT', '5432'))
@click.option("--user", required=True, default=lambda: os.environ.get('DEDDIAG_DB_USER', 'postgres'))
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
@click.option("--user", required=True, default=lambda: os.environ.get('DEDDIAG_DB_USER', 'postgres'))
@click.option("--password", hide_input=True, default=lambda: os.environ.get('DEDDIAG_DB_PW'), show_default='')
@click.option("--format", "print_format", type=click.Choice(["str", "latex"]), default="str")
@click.option("--include-annotations", is_flag=True,
              help="Include annotation count column")
@click.option("--include-missing", is_flag=True,
              help="Include missing data column. WARNING: Query may take some time")
@click.option("--query-cache", type=str, help="Query cache where required queries are cached to speed up")
def stats(host, db, user, port, password, print_format, include_annotations, include_missing, query_cache):
    """Print dataset stats"""
    from . import Connection, Houses, Items, MeasurementsRange, Annotations, MeasurementsMissing
    from ._formatter import StringFormatter, LatexFormatter
    import pandas as pd
    con = Connection(host, port, db, user, password)
    items = Items().request(con, cache_dir=query_cache)
    columns = ["House", "Item", "Name", "First date", "Last date", "Duration"]
    if include_annotations:
        columns += ["Annotations"]
    if include_missing:
        logging.warning("Including missing measurements stats, this will take some time!")
        columns += ["Missing > 1h5min", "Missing > 1day"]

    data = []
    for _, house in Houses().request(con, cache_dir=query_cache).iterrows():
        house_id = f"House {house.id:2}"
        for _, item in items.loc[items.house == house.id].iterrows():
            m_range = MeasurementsRange(item['id']).request(con, cache_dir=query_cache)

            line = [
                house_id,
                item['id'],
                item['name'],
                str(m_range.min_date.item()),
                str(m_range.max_date.item()),
                f"{(m_range.max_date.item() - m_range.min_date.item()).days} days"
            ]
            if include_annotations:
                annotations = Annotations(item_id=item['id']).request(con, cache_dir=query_cache)
                line += [str(len(annotations))]
            if include_missing:
                missing = MeasurementsMissing(item_id=item['id']).request(con, cache_dir=query_cache)
                line += [
                    "{:.2f}%".format(missing.perc_missing_hour.item() * 100),
                    "{:.2f}%".format(missing.perc_missing_day.item() * 100)
                ]

            data.append(line)
    df = pd.DataFrame(data, columns=columns).set_index(["House", "Item"])
    df.to_latex()
    formatter = None
    formatter_kwargs = {}
    if print_format == "str":
        formatter = StringFormatter()
    elif print_format == "latex":
        formatter = LatexFormatter()
        formatter_kwargs = {'alignment': "|c|l|l|c|c|c|" + "c|" * sum([include_missing, include_annotations])}

    if formatter is not None:
        formatter.print(df, **formatter_kwargs)

