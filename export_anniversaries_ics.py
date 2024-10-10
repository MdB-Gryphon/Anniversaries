from datetime import date, timedelta, datetime
import uuid

# Define ICS file headers
ics_content = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Home Assistant//Anniversary Calendar Export//EN",
    "METHOD:PUBLISH"
    "X-WR-CALNAME:HA Verjaardagen",
    "NAME:HA Verjaardagen",
    "REFRESH-INTERVAL;VALUE=DURATION:P12H",
    "CALSCALE:GREGORIAN",
    "BEGIN:VTIMEZONE",
    "TZID:Europe/Brussels",
    "TZURL:https://www.tzurl.org/zoneinfo-outlook/Europe/Brussels",
    "X-LIC-LOCATION:Europe/Brussels",
    "BEGIN:DAYLIGHT",
    "TZNAME:CEST",
    "TZOFFSETFROM:+0100",
    "TZOFFSETTO:+0200",
    "DTSTART:19700329T020000",
    "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU",
    "END:DAYLIGHT",
    "BEGIN:STANDARD",
    "TZNAME:CET",
    "TZOFFSETFROM:+0200",
    "TZOFFSETTO:+0100",
    "DTSTART:19701025T030000",
    "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU",
    "END:STANDARD",
    "END:VTIMEZONE",
]

# Get all entities from Home Assistant
all_states = hass.states.all()

# Filter entities that start with 'sensor.anniversary'
anniversary_sensors = [state for state in all_states if state.entity_id.startswith('sensor.anniversary_')]

# Example: loop through and print the entity ID and state of each sensor
for sensor in anniversary_sensors:
    #logger.warning(f"{sensor.entity_id}")

    # Fetch the anniversary calendar entity
    anniversary_calendar = hass.states.get(sensor.entity_id)

    # Ensure the entity exists and contains the expected data
    if anniversary_calendar:
        # Check if the state contains the attributes we expect
        attributes = anniversary_calendar.attributes
        if 'friendly_name' in attributes:
            # Create an event dictionary from attributes
            summary = attributes.get('friendly_name')
            start_time = attributes.get('next_date')  
            formatted_start = start_time.strftime('%Y%m%d')
            end_time = start_time + timedelta(days=1)
            formatted_end = end_time.strftime('%Y%m%d')
            guid = uuid.uuid5(uuid.NAMESPACE_DNS, sensor.entity_id)
            dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            if 'years_at_anniversary' in attributes:
                years_at_anniversary = attributes.get('years_at_anniversary') 
                summary = f"{summary} ({years_at_anniversary})"

            # Define ICS event
            ics_event = [
                "BEGIN:VEVENT",
                f"SUMMARY:{summary}",
                f"DTSTART;VALUE=DATE:{formatted_start}",
                f"DTEND;VALUE=DATE:{formatted_end}",
                f"DESCRIPTION:",
                f"UID:{guid}",
                f"DTSTAMP:{dtstamp}",
                "END:VEVENT",
            ]

            ics_content.extend(ics_event)

        else:
            # Log warning if attributes are missing
            logger.warning("The calendar entity does not have the expected attributes.")

# End ICS file
ics_content.append("END:VCALENDAR")

# Write to ICS file
with open("/config/www/anniversaries.ics", "w", encoding="utf-8", newline='') as f:
    f.write("\r\n".join(ics_content))
