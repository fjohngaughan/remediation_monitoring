# GecMonitor

Visit the website at https://www.gecmonitor.com
<br>
<br>
Written in Python, HTML, and CSS, with Flask, Selenium Web Driver, and Bootstrap.

## The Problem
California's state government has a database called <a href="https://geotracker.waterboards.ca.gov">GeoTracker</a> to track water pollution cleanup projects. It's a good 
website for tracking one or two sites at a time, but there's no clean, efficient way to track updates on several sites. Organizations have limited and fairly inconvenient options: 
1) Click through the same pages on GeoTracker month after month, looking for new information; 
2) Sign up for email alerts for each site individually and deal with sporadic 
emails whenever something new is posted on a particular site; or, 
3) Build a custom dashboard that makes use of the .txt files containing all project data that GeoTracker offers for download and updates periodically.

None of these solutions are particularly convenient. In an ideal world, users would be able to check for updates on every site they're interested in with a single click, and get a one-page
report of any changes. 


## The Solution
That's where GecMonitor comes in. We allow users to group the cleanup projects they track into reports. When they request an update on a report, GecMonitor scans for new information 
and gives them a clean, simple update with any new activities and documents, organized by site.
<br>
<br>
To put it simply, it checks all your sites for you and gives you any new information and documents on a single page.
<br>
<br>
## Where We Are & What's Ahead
For now, GecMonitor tracks a site's status and new actions in the “Regulatory Activities” tab on GeoTracker.
<br>
In the near future, we plan to: 
<ul> 
  <li>expand the type of information our reports can monitor on GeoTracker (Cleanup Action Reports, Environmental Data, Site Maps / Documents, Community Involvement, etc.) </li>
  <li>incorporate EnviroStor data</li> 
  <li>make it a lot faster to get report updates by, 1) leveraging fairly comprehensive datasets updated daily by GeoTracker and EnviroStor, and 2) using distributed web scraping for other needed data</li>
  <li>rebuild the front end with React</li>
  <li>add unit tests and error handling</li>
  <li>switch from Flask to Django</li>
</ul>
The broader vision is to make our reports the hub for personalized updates on cleanup sites, drawing information from GeoTracker, EnviroStor, and city meeting agendas and minutes (and maybe online news). 
That’s actually where were got the “Gec” in “GecMonitor”:
<br>
<br>
<strong>G</strong>eoTracker
<br>
<strong>E</strong>nviroStor
<br>
<strong>City</strong> meeting agendas and minutes
<br>
<br>
To sum up: GecMonitor is here so you can spend less time looking for information about pollution cleanup projects, and more time using it.
