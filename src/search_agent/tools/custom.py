from datetime import datetime, date
from typing import Dict, Any

def get_current_date() -> Dict[str, Any]:
    """
    Get the current date.

    Returns:
        Dict[str, Any]: A dictionary containing the current date as a string.
    """
    current_date = date.today().isoformat()
    return {"current_date": current_date}

def calculate_date_interval(start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Calculate the interval between two dates.

    Args:
        start_date (str): The start date in ISO format (YYYY-MM-DD).
        end_date (str): The end date in ISO format (YYYY-MM-DD).

    Returns:
        Dict[str, Any]: A dictionary containing the number of days between the dates.
    """
    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        interval = (end - start).days
        return {"interval_days": interval}
    except ValueError:
        return {"error": "Invalid date format. Please use YYYY-MM-DD."}