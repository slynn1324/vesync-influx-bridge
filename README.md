# vesync-influx-bridge

Simple python script that polls the vesync api (derived from pyvesync) to extract information from VeSync devices.  Currently only tested with a Vital 200S Air Filter.

## Building
```
./build.sh
```

## Running
```
podman run -d \
	--name "vesync-influx-bridge" \
	--restart=unless-stopped \
	-e INFLUXDB_URL='...' \
	-e INFLUXDB_TOKEN='...' \
	-e VESYNC_EMAIL='...' \
	-e VESYNC_PASSWORD='...' \ 
	vesync-influx-bridge
```
