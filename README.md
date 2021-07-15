# deddiag-loader
Dataloader for DEDDIAG, a Domestic Energy Demand Dataset of Individual Appliances Germany.

The dataset contains recordings of 15 homes over a period of up to 3.5 years, wherein total 50 appliances have been recorded at a frequency of 1 Hz. Recorded appliances are of significance for load-shifting purposes such as dishwashers, washing machines and refrigerators. One home also includes three-phase mains readings that can be used for disaggregation tasks. Additionally, DEDDIAG contains manual ground truth event annotations for 14 appliances, that provide precise start and stop timestamps.

The dataset is available for download on Figshare: [10.6084/m9.figshare.13615073.v1](https://doi.org/10.6084/m9.figshare.13615073.v1).
For a detailed description of the dataset please see [this publication](https://doi.org/10.1038/s41597-021-00963-2).


## Install
The deddiag-loader is available on [pypi](https://pypi.org/project/deddiag-loader/)

```
pip install deddiag-loader
```

### Install from source (alternative)
```
python setup.py install
```

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

## Citation
When using the dataset in academic work please cite [this paper](https://doi.org/10.1038/s41597-021-00963-2) as the reference.
```
@article{DEDDIAG_2021,
    authors={Wenninger, Marc and Maier, Andreas and Schmid, Jochen},
    title={DEDDIAG, a domestic electricity demand dataset of individual appliances in Germany},
    journal={Scientific Data},
    year={2021},
    month={Jul},
    doi={https://doi.org/10.1038/s41597-021-00963-2}
}
```

## Acknowledgements
The monitoring system and dataset were created as part of a research project of the [Technical University of Applied Sciences Rosenheim](https://www.th-rosenheim.de/).

The project was funded by the [German Federal Ministry of Education and Research (BMBF)](https://www.bmbf.de/), grant 01LY1506,
and supported by the [Bayerische Wissenschaftsforum (BayWISS)](https://www.baywiss.de/).

![](https://www.th-rosenheim.de/typo3conf/ext/in2template/Resources/Public/Images/logo-th-rosenheim-2019.png)


## License
MIT licensed as found in the [LICENSE](LICENSE) file.
