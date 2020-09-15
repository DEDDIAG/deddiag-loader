# deddiag-loader
Dataloader for DEDDIAG, a Domestic Energy Demand Dataset of Individual Appliances Germany.

## Install

python setup.py install

## CLI Usage

Show Dataset overview
```bash
python -m deddiag_loader stats --host=localhost --password=<password>
```

Save measurements with labels to numpy array
```bash
python -m deddiag_loader save --host=localhost --password=<password>
```

The database options can also be provided using environment variables:
```bash
DEDDIAG_DB_PW=
DEDDIAG_DB_USER=
DEDDIAG_DB_HOST=
DEDDIAG_DB_NAME=
```

## Code Example

```python
from deddiag_loader import Connection, Annotations, MeasurementsExpandedWithLabels
con = Connection(password="password")
item_id = 10

start_date = "2016-11-30T20:24:05"
stop_date = "2019-06-02T17:56:17"

annotations = Annotations(item_id, start_date=start_date, stop_date=stop_date).request(con)
first_annotation = annotations.iloc[0]

# Get Expanded Measurements for first annotation
measurements = MeasurementsExpandedWithLabels(item_id, first_annotation['label_id'], first_annotation['start_date'], first_annotation['stop_date']).request(con)
```

## Acknowledgements
The monitoring system and dataset were created as part of a research project of the [Technical University of Applied Sciences Rosenheim](https://www.th-rosenheim.de/).

The project was funded by the [German Federal Ministry of Education and Research (BMBF)](https://www.bmbf.de/), grant 01LY1506,
and supported by the [Bayerische Wissenschaftsforum (BayWISS)](https://www.baywiss.de/).

![](https://www.th-rosenheim.de/typo3conf/ext/in2template/Resources/Public/Images/logo-th-rosenheim-2019.png)


## License
MIT licensed as found in the [LICENSE](LICENSE) file.
