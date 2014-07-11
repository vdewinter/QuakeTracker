import model, csv

def load_quakes(session):
    with open('./seed_data/signif.csv', 'rb') as f:
        rows = csv.reader(f, delimiter=",")
        next(rows, None) # skip header
        for r in rows:
            r_id = r[0]
            r_tsunami = r[1]
            r_year = r[2]
            r_month = r[3]
            r_day = r[4]
            r_hour = r[5]
            r_magnitude_mw = r[9]
            r_magnitude_ms = r[10]
            r_magnitude_mb = r[11]
            r_magnitude_ml = r[12]
            r_magnitude_mfa = r[13]
            r_magnitude_unk = r[14]
            r_latitude = r[19]
            r_longitude = r[20]
            q = model.Quake(id = r_id, tsunami = r_tsunami, 
                year = r_year, month = r_month, day = r_day, hour = r_hour, 
                magnitude_mw = r_magnitude_mw, magnitude_ms = r_magnitude_ms,
                magnitude_mb = r_magnitude_mb, magnitude_ml = r_magnitude_ml, 
                magnitude_mfa = r_magnitude_mfa, magnitude_unk = r_magnitude_unk, 
                latitude = r_latitude, longitude = r_longitude)
            session.add(q)
        session.commit()

def load_tsunamis(session):
    with open('./seed_data/tsrunup.csv', 'rb') as f:
        rows = csv.reader(f, delimiter=",")
        next(rows, None) # skip header
        for r in rows:
            r_id = r[0]
            r_tseventid = r[1]
            r_year = r[2]
            r_month = r[3]
            r_day = r[4]
            r_doubtful = r[5]
            r_latitude = r[9]
            r_longitude = r[10]
            r_distance_from_source = r[12]
            r_travel_time_hours = r[13]
            r_travel_time_minutes = r[14]
            r_water_height = r[15]
            r_horizontal_innundation = r[16]
            r_period = r[18]
            t = model.Tsunami(id = r_id, tseventid = r_tseventid, year = r_year, day = r_day,
                doubtful = r_doubtful, latitude = r_latitude, longitude = r_longitude,
                distance_from_source = r_distance_from_source, travel_time_hours = r_travel_time_hours,
                travel_time_minutes = r_travel_time_minutes, water_height = r_water_height,
                horizontal_innundation = r_horizontal_innundation, period = r_period)
            session.add(t)
        session.commit()

def main(session):
    load_quakes(session)
    load_tsunamis(session)

if __name__ == "__main__":
    s = model.connect()
    main(s)