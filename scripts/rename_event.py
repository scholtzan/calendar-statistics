"""This automatically renames Google Calendar events matching a regex."""

import click
from datetime import date, datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import re

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


@click.command()
@click.option("--credentials", help="Path to credential file", required=True)
@click.option(
    "--cache_file", "--cache-file", default="/tmp/token.pickle", required=True
)
@click.option(
    "--start",
    type=click.DateTime(
        formats=["%Y-%m-%d"],
    ),
    default=str(date(2021, 1, 1)),
    help="Start date from when events should be updated.",
)
@click.option(
    "--end",
    type=click.DateTime(
        formats=["%Y-%m-%d"],
    ),
    default=str(date.today()),
    help="Start date from when events should be updated.",
)
@click.option(
    "--regex", help="Regex to match strings that will be replaced", required=True
)
@click.option(
    "--replacement",
    help="New string that will replace string matching regex",
    required=True,
)
@click.option("--calendar", help="Name of the calendar to update", required=True)
@click.option(
    "--dryrun",
    help="Run rename script without applying updates",
    default=False,
    is_flag=True,
)
def rename(credentials, cache_file, start, end, regex, replacement, calendar, dryrun):
    service = get_api_service(cache_file, credentials)
    calendar_id = get_calendar(calendar, cache_file, credentials)

    start = start.isoformat() + "Z"
    end = end.isoformat() + "Z"
    events_request = service.events().list(
        calendarId=calendar_id,
        timeMin=start,
        timeMax=end,
        singleEvents=True,
    )

    while events_request is not None:
        events_result = events_request.execute()

        for event in events_result.get("items", []):
            name = re.sub(regex, replacement, event["summary"], flags=re.IGNORECASE)
            if name != event["summary"]:
                if not dryrun:
                    click.echo(
                        f"Update {event['summary']} ({event['start']}) to {name}"
                    )
                    event["summary"] = name
                    service.events().update(
                        calendarId=calendar_id, eventId=event["id"], body=event
                    ).execute()
                else:
                    click.echo(
                        f"Would update {event['summary']} ({event['start']}) to {name}"
                    )

        events_request = service.events().list_next(events_request, events_result)


def get_api_service(cache_file, credentials_file):
    creds = None

    if os.path.exists(cache_file):
        with open(cache_file, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(cache_file, "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)
    return service


def get_calendar(name: str, cache_file, credentials_file):
    """Return the calendar ID."""
    service = get_api_service(cache_file, credentials_file)
    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get("items", [])

    for calendar in calendars:
        if calendar.get("summary", "") == name:
            return calendar.get("id", None)

    return None


if __name__ == "__main__":
    rename()
