from datetime import datetime, timedelta


def format_time(raw_time):
    # Format has to be '• time'
    if "•" not in raw_time:
        return None

    time_parts = raw_time.split("•")

    if len(time_parts) > 1:
        cleaned_time = time_parts[-1].strip()
    else:
        cleaned_time = raw_time

    if not cleaned_time:
        return None

    if "hours" in cleaned_time or "minutes" in cleaned_time:
        published_date = datetime.now()
    elif "yesterday" in cleaned_time:
        published_date = datetime.now() - timedelta(days=1)
    elif "days" in cleaned_time:
        days = int(cleaned_time.split(" ")[0])
        published_date = datetime.now() - timedelta(days=days)
    else:
        # Disregard dates past a month
        return None

    return published_date
