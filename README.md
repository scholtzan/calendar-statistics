# Calendar Statistics

[todo: link blog post]

Calendars are a convenient mechanism for tracking how time is spent. This repository contains tooling to generate a dashboard that provides insight into activity event data recorded through Google Calendar. 

The dashboard shows information about:
* How much time was spent on each category?
* What activities was most time spent on?
* How many context switches did occur in a gived time period?
* ...

Activity data for specific time periods can be analyzed through dashboard filters. Different types of aggregations are automatically computed, such as daily, weekly or overall results for the selected time period. It is possible to see how much absolute time has been spent as well as a relative breakdown (%).

<img src="https://github.com/scholtzan/calendar-statistics/raw/main/img/dashboard.png" width="1000">
*Dashboard*


## Time Tracking

Activity data can be tracked through multiple Google Calendars. Each calendar represents a broad **category**, such as _Focused Work_, _Meetings_ or _Social_. Each event that gets added to these calendars is tagged with an **area** and has a **description** of the activity or task that was performed. Areas could refer to a project or some specific effort for which a variety of activities have and/or will be performed. The area and description are specified in the event title. By default, the following format is expected for event titles: _<area> - <description>_. Generally, the description is optional and if no description is provided then ` - ` can be removed. 

As an example, of what this would look like for a specific day with multiple tracked activities:

<img src="https://github.com/scholtzan/calendar-statistics/raw/main/img/calendar.png" width="1000">

This example has two calendars which divide activities into _Meetings_ and _Focused Work_. Several areas that, refer to projects or other efforts (_Project Hydra_, _Project Copernicu_, _Knowledge Sharing_, ...) are being defined to further categorize specific activities.

## Setup

To get access to the calendar data through the Google Calendar API, first an [API key needs to be generated](https://docs.simplecalendar.io/google-api-key/). The created credentials need to be stored locally.

To get the dashboard:

```
pip install -r requirements.txt 
export CALSTATS_CREDENTIALS='/path/to/credentials.json'
export CALENDARS='["Meetings", "Work"]'
voila calstats.ipynb --theme=dark
```

A new browser window will be opened automatically that will show the dashboard.

A Docker image can also be created and run via:

```
docker build -t calendar-insights . 
docker run   -it  --mount type=bind,source=/path/to/credentials.json,target=/root/app/credentials.json --mount type=bind,source=/tmp/token.pickle,target=/tmp/token.pickle -p 7777:7777 calendar-insights
```

## Configuration

The dashboard can either be configured through changing the configuration parameters in `calstats.ipynb` or by setting the following environment variables:

* `CALSTATS_CREDENTIALS` - Path to were API credentials are stored [required]
* `CALENDARS` - A JSON list with the names of the calendars which should be analyzed as part of the dashboard
* `ACTIVITY_REGEX` - Regex that defines how the area and description should be parsed from the event titles. By default the format _<area> - <description>_ is assumed
* `CACHE_FILE` - Local path to where API token should be stored. Default is `/tmp/token.pickle`


## Adding More Insights

The dashboard can be extended in `calstats.ipynb` and more graphs can be added. Adding a new visualization is supported by adding a new cell to the notebook which specifies a new class that extends `ActivityVisualization`:

```python
class NewVisualization(ActivityVisualization):
    @property
    def title(self):
        return "Some new visualization" # This is shown as the title above the graph on the dashboard

    @property
    def description(self):
        return "Some description" # This is shown below the title on the dashboard

    def process(self):
        for calendar, calendar_data in self.activities.items():  # self.activities contains activity data as Activity objects
            # some processing
        self.data = ... # data that is plotted in the graph

    def aggregate_data(self):
        # to define custom aggregations; default is total and percentage
        pass

    def plot(self):
        # code to plot the data
        # by default data is plotted as a bar chart
        pass 
```

Calendar data is available in `self.activities` as `Activity` instances:

```python
class Activity:
    category: str 
    start: datetime 
    end: datetime 
    name: Optional[str] 
    description: Optional[str]
```

The data gets first processed in the `process()` method, which is where the analysis logic needs to be implemented. Providing a custom implementation for `aggregate_data()` and `plot()` is optional. `aggregate_data()` aggregates the processed data in different ways, such as computing percentages from absolute values. `plot()` allows to define how the processed and aggregated data should be displayed.

The dashboard allows to select different analysis periods which will result in data being shown day-by-day, week-by-week or as an overall result for the current time period. The pre-computed periods are part of `ActivityVisualization` and can be accessed through `self.get_periods()`.
