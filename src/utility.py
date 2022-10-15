second_multiplier = [
    1, # seconds
    60, # minutes
    3_600, # hours
    86_400, # days
]

def timestamp_to_seconds(timestamp: str) -> int:
    """ Try to convert a timestamp string (e.g., 3:45) to seconds. """
    split = timestamp.split(":")
    split.reverse()

    split = split[:len(second_multiplier)]

    total_seconds = 0

    for index, item in enumerate(split):
        total_seconds += int(item) * second_multiplier[index]
    
    return total_seconds
