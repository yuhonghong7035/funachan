import datetime

from ..utils import memoize, get_google_client


@memoize
def fetch_jp_holidays(date=datetime.date.today(), n=25):
    """date以降の祝日をn件返す"""
    
    service = get_google_client()
    response = service.events().list(
        calendarId='ja.japanese#holiday@group.v.calendar.google.com',
        timeMin=date.isoformat() + 'T00:00:00.000000Z',
        maxResults=n
    ).execute()
    events = response.get('items', [])
    return sorted([e['start']['date'] for e in events])


@memoize
def is_holiday(date: datetime.date) -> bool:
    def is_weekend():
        return date.weekday() in (5, 6)
    
    def is_jp_holiday():
        return date.isoformat() in fetch_jp_holidays()
    
    return is_weekend() or is_jp_holiday()


@memoize
def before_holiday(date: datetime.date) -> bool:
    tomorrow = date + datetime.timedelta(days=1)
    return (not is_holiday(date)) and is_holiday(tomorrow)
