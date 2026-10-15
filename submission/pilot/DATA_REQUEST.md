# Proposed request for campus transport history

**Draft only. Not sent to anyone.** Intended recipient: the campus transport office or data owner.

Purpose: evaluate an operator planning prototype in shadow mode, with no connection to live dispatch. Please first confirm that the data may be shared and identify any access, retention or confidentiality requirements.

Requested fields:

| Dataset | Required content | Units and validation |
|---|---|---|
| Stops | stable stop ID, name, coordinates | WGS84 latitude/longitude; unique IDs |
| Route graph | directed origin/destination stop IDs, distance, typical travel time | kilometres and minutes; connected paths |
| Timetable | trip ID, route ID, vehicle ID, date, departure and allowed window | explicit timezone; actual dates, not synthetic offsets |
| Fleet | vehicle ID, permitted capacity, availability, depot, confirmed duty rules | passenger count; time intervals; operator-confirmed limits |
| Vehicle observations | vehicle/trip ID, timestamp, latitude, longitude, quality if available | timestamps with timezone; document sampling frequency |
| Stop counts | time interval, stop and route/direction, boarding, alighting, observed queue | counts; define missing values separately from zero |
| Disruption log | affected vehicle/segment, start/end, known-at time, reason | distinguish planned information from later ground truth |

Passenger identities, phone numbers, individual travel histories and payment details are not requested. Transfer outcomes should be aggregate counts where feasible. State the origin and measurement method of each dataset and distinguish measured from inferred values.

A usable chronological period must support an earlier calibration split and a later untouched evaluation split. Agree the actual duration with the data owner based on availability and variation. No data adapter or real-campus deployment is claimed in the current MVP; formats and missing operating constraints must be reviewed before integration.
