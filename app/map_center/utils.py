from collections import Counter

from app.database.queries import get_dataset


def generate_dataset_steps(dataset_hash):
    row_data = get_dataset(dataset_hash, rows_limit=20)

    lon_steps, lat_steps = [], []
    for index, (lon, lat, _) in enumerate(row_data):
        if index == 18:
            break
        lon_steps.append(abs(lon - row_data[index + 1][0]))
        lat_steps.append(abs(lat - row_data[index + 1][1]))

    steps = {"lon": Counter(lon_steps).most_common(1)[0][0], "lat": Counter(lon_steps).most_common(1)[0][0]}
    return steps
