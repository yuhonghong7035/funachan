import datetime

from .utils import is_holiday, before_holiday
from ..utils import get_config, get_slack_users
from ..utils import get_google_client, get_slack_client


class HolidayReporter(object):
    def __init__(self):
        self.slack = Slack()
        self.calendar = Calendar()
    
    def question(self, channel_name):
        date = datetime.date.today()
        if not before_holiday(date):
            return
        
        response = []
        while True:
            date += datetime.timedelta(days=1)
            if is_holiday(date):
                response.append(self.slack.post(channel_name, date))
            else:
                break
    
    def report(self):
        pass


class Slack(object):
    def __init__(self):
        self.client = get_slack_client()
    
    def post(self, channel_name, date):
        template = '%Y-%m-%d (%a) 来る人！'
        response = self.client.chat.post_message(
            channel=channel_name,
            text=date.strftime(template),
            as_user=True)
        
        channel_id = response.body['channel']
        timestamp = response.body['ts']
        return (channel_id, timestamp)
    
    def fetch_reacted_users(self, channel_id, timestamp):
        response = self.client.reactions.get(
            channel=channel_id,
            timestamp=timestamp
        )
        reactions = response.body['message'].get('reactions', None)
        if reactions is None:
            return
        
        user_ids = []
        for r in reactions:
            user_ids += r['users']
        user_names = [get_slack_users()[u] for u in set(user_ids)]
        return user_names


class Calendar(object):
    def __init__(self):
        self.client = get_google_client()
    
    def add(self, date, users):
        self.client.events().insert(
            calendarId=get_config()['overtime_calendar_id'],
            body={
                'summary': ', '.join(users),
                'start': {
                    'dateTime': date.isoformat() + 'T09:00:00',
                    'timeZone': 'Asia/Tokyo'
                },
                'end': {
                    'dateTime': date.isoformat() + 'T18:00:00',
                    'timeZone': 'Asia/Tokyo'
                }
            }
        ).execute()
