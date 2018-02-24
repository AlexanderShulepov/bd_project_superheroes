#!/bin/bash
psql -U postgres -d "geo2.0" -c "Select * from clearingalarm()"
psql -U postgres -d "geo2.0" -c "Select * from clearinghero()"
psql -U postgres -d "geo2.0" -c "Select * from gogo()"
