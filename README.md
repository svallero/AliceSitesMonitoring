# AliceSitesMonitoring
Jupyter Lab notebook to produce some summary plot.

Requisites:
- Jupyter Lab
- Docker
- Python packages: lxml, pandas, matplotlib

### Start Jupyter Lab 
 
 From the local folder run:
 
 ```
 jupyter lab
 ```

### Deploy InfluxDB (optional)
From the folder _influx_ run:

```
./run.sh
./create_db.sh
```

### Deploy Grafana (optional)

From the folder _grafana_ run:

```
./run.sh
```

