from ._cache import QueryCache


class Query(object):
    """
    Base Query functionality

    This may be used by inheriting from Query and overriding _QUERY.
    parameters are passed by overriding __init__ and assigning values to the self_params dict.

    Example:
        class SampleQuery(Query):
            _QUERY = "SELECT * FROM table"
    """
    _QUERY = None

    def __init__(self):
        self._params = {}

    def request(self, con, cache_dir=None):
        q = self._format_sql()
        if cache_dir is not None:
            try:
                return QueryCache(cache_dir).read(q)
            except FileNotFoundError:
                pass
        df = con.from_psql(q)
        if cache_dir is not None:
            QueryCache(cache_dir).save(q, df)
        return df

    def _format_sql(self):
        return self._QUERY.format(**self._params)


class Houses(Query):
    """Query all houses and persons information"""
    _QUERY = "SELECT * FROM houses"


class Items(Query):
    """Query all items"""
    _QUERY = "SELECT * FROM items"


class AnnotationLabels(Query):
    """Query all annotation labels"""
    _QUERY = "SELECT * FROM annotation_labels"


class Annotations(Query):
    """Query annotation"""
    _QUERY = "SELECT * FROM annotations WHERE item_id={item_id} " \
             "and start_date >= {start_date} " \
             "and stop_date <= {stop_date} " \
             "{label_id}" \
             "ORDER BY start_date"

    def __init__(self, item_id, label_ids=None, start_date=None, stop_date=None):
        """
        Query annotation of given item
        :param item_id: item_id associated with annotation
        :param label_ids: list of label_ids associated with annotation. If None all annotations of item_id are returned
        :param start_date: Start of first annotation
        :param stop_date: End of last annotation
        """
        start_date = f"'{start_date}'" if start_date is not None else "to_timestamp(0)"
        stop_date = f"'{stop_date}'" if stop_date is not None else "to_timestamp('inf')"
        self._params = {
            'item_id': item_id,
            'start_date': start_date,
            'stop_date': stop_date,
            'label_id': f"and label_id in ({','.join(label_ids)})" if label_ids is not None else ""
        }


class MeasurementsExpanded(Query):
    """Get second based measurements"""
    _QUERY = "SELECT * FROM get_measurements('{item_id}','{start_date}','{stop_date}')"

    def __init__(self, item_id, start_date, stop_date):
        """
        Get measurement at every second for given item_id
        :param item_id: item_id
        :param start_date: First measurement
        :param stop_date: Last measurement
        """
        self._params = {
            'item_id': item_id,
            'start_date': start_date,
            'stop_date': stop_date
        }


class Measurements(Query):
    """Get second based measurements"""
    _QUERY = """
    SELECT * FROM measurements 
    WHERE item_id = '{item_id}' and time between '{start_date}' and '{stop_date}'
    ORDER by time
    LIMIT {limit}
    """

    def __init__(self, item_id, start_date, stop_date, limit=None):
        """
        Get measurement at every second for given item_id
        :param item_id: item_id
        :param start_date: First measurement
        :param stop_date: Last measurement
        """
        self._params = {
            'item_id': item_id,
            'start_date': start_date,
            'stop_date': stop_date,
            'limit': 'ALL' if limit is None else limit
        }


class MeasurementsExpandedWithLabels(Query):
    """Get second based measurements and available annotation labels at each time step"""
    _QUERY = "SELECT *, " \
             "(SELECT count(label_id) FROM annotations " \
             "WHERE item_id = q0.item_id {label_id} " \
             "and (annotations.start_date <= q0.time and q0.time <= annotations.stop_date)) > 0 as labels " \
             "FROM get_measurements('{item_id}','{start_date}','{stop_date}') q0"

    def __init__(self, item_id, label_id, start_date, stop_date):
        """
        Get second based measurements and available labels at each time step
        Rows are returned as: [item_id, time, value, [label_id, label_id, ...]]
        :param item_id: item_id
        :param label_id: List of label ids as integers or None
        :param start_date: First measurement
        :param stop_date: Last measurement
        """
        self._params = {
            'item_id': item_id,
            'label_id': f"and label_id in ({','.join(label_id)})" if label_id is not None else "",
            'start_date': start_date,
            'stop_date': stop_date
        }


class MeasurementsRange(Query):
    """Range of measurements for given item_id"""
    _QUERY = "SELECT DISTINCT round_timestamp(min(time)) as min_date, " \
             "round_timestamp(max(time)) as max_date " \
             "FROM measurements WHERE item_id='{item_id}'"

    def __init__(self, item_id):
        """
        Range of measurements for given item_id
        :param item_id: item_id
        """
        self._params = {
            'item_id': item_id
        }


class MeasurementsMissing(Query):

    _QUERY = """
    with
     v_min_max as (SELECT DISTINCT max(time) - min(time) as time_total FROM measurements WHERE item_id={item_id}),
     v_lag as (SELECT time, time - LAG(time) OVER (ORDER BY time) as time_diff FROM measurements WHERE item_id={item_id}),
    SELECT 
        DISTINCT
       {item_id} as item_id,
       v_min_max.time_total,
       v_lag.time_diff
    FROM 
     v_min_max,
     v_lag
    WHERE time_diff > '{threshold}'
    """

    def __init__(self, item_id, threshold='1hour 5min'):
        """
        Additional information for measurements of given item_id
        :param item_id: item_id
        """
        self._params = {
            'item_id': item_id,
            'threshold': threshold
        }


class MeasurementsMissingTotal(Query):

    _QUERY = """
    with
     v_min_max as (SELECT DISTINCT max(time) - min(time) as time_total FROM measurements WHERE item_id={item_id}),
     v_lag as (SELECT time, time - LAG(time) OVER (ORDER BY time) as time_diff FROM measurements WHERE item_id={item_id}),
     v_hour_missing as (SELECT DISTINCT sum(EXTRACT(EPOCH FROM time_diff)) as missing FROM v_lag WHERE time_diff > '1hour 5sec'),
     v_day_missing as (SELECT DISTINCT sum(EXTRACT(EPOCH FROM time_diff)) as missing FROM v_lag WHERE time_diff > '1 day')
    SELECT 
        DISTINCT
       {item_id} as item_id,
       v_min_max.time_total,
       COALESCE(v_hour_missing.missing, 0) / EXTRACT(EPOCH FROM v_min_max.time_total) as perc_missing_hour,
       COALESCE(v_day_missing.missing, 0) / EXTRACT(EPOCH FROM v_min_max.time_total) as perc_missing_day
    FROM 
     v_min_max,
     v_hour_missing,
     v_day_missing;
    """

    def __init__(self, item_id):
        """
        Additional information for measurements of given item_id
        :param item_id: item_id
        """
        self._params = {
            'item_id': item_id
        }
