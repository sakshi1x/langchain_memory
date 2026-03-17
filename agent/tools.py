from langchain.tools import tool

@tool
def write_email(to: str, subject: str, content: str) -> str:
    """
    Sends an email to the specified recipient with the given subject and content.

    Args:
        to (str): The recipient's email address.
        subject (str): The subject of the email.
        content (str): The body content of the email.

    Returns:
        str: Confirmation message indicating the email was sent.
    """
    return f"Email sent to {to} with subject '{subject}'"

@tool
def schedule_meeting(attendees: list[str], subject: str, duration_minutes: int, preferred_day: str) -> str:
    """
    Schedules a meeting with the specified attendees, subject, duration, and preferred day.

    Args:
        attendees (list[str]): List of attendees' names or email addresses.
        subject (str): The subject or title of the meeting.
        duration_minutes (int): Duration of the meeting in minutes.
        preferred_day (str): The preferred day for the meeting.

    Returns:
        str: Confirmation message with meeting details.
    """
    return f"Meeting '{subject}' scheduled for {preferred_day} with {len(attendees)} attendees"

@tool
def check_calendar_availability(day: str) -> str:
    """
    Checks the calendar for available time slots on the specified day.

    Args:
        day (str): The day to check availability for.

    Returns:
        str: A list of available time slots on the specified day.
    """
    return f"Available times on {day}: 9:00 AM, 2:00 PM, 4:00 PM"