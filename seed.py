import model, json

def load_quakes(session):
    with open('./static/seed_data/historical_quakes_500.json') as f:
        decoded_json = json.load(f)
        counter = 0 

        for r in decoded_json["features"]:
            id = r["id"]
            timestamp = r["properties"]["time"]
            updated = r["properties"]["updated"]
            magnitude = r["properties"]["mag"]
            longitude = r["geometry"]["coordinates"][0]
            latitude = r["geometry"]["coordinates"][1]
            tsunami = r["properties"]["tsunami"]

            if not magnitude:
                continue
                         
            q = model.Quake(id = id, timestamp = timestamp, updated = updated,
                magnitude = magnitude, longitude = longitude, latitude = latitude,
                tsunami = tsunami)

            session.add(q)
            counter += 1

            if counter > 50:
                session.commit()
                counter = 0

def main(session):
    model.Base.metadata.create_all(bind=model.engine)
    load_quakes(session)

if __name__ == "__main__":
    main(model.session)
