# filtertube

## what? 

This project's main file `filtertube.py` is a Flask application that sets up an listening endpoint to receive inbound POST with details about a user and the YouTube video that they want.  The user's request is written to a SQL database in a "Pending" state where one of the views in the app is to list out all the pending requests for an admin to approve/deny.   The approval/denial only changes the 'status' of that request to "Approved"  which is what the separate `downloader.py` watches for.   The downloader finds approved requests and then actually downloads them to a local user folder, and after downloading there's a mechanism to copy them to another folder which for me is where my media is served to my users. 

## why? 

YouTube's parental control offerings suck. YouTube restricted mode has content I don't want my kids seeing, and YouTube kids is leaky and not age appropriate for some of my older ones.   So... I wanted per-video veto power over what my kids watch.  My kids have permission to come into my office and use a computer to browse YouTube, skimming content, but not full on watching it.  Instead when they find a video they'd like to watch, they click a little bookmarklet button "Request Video Kidname" which uses some JS to gather the YouTube video link and the kids name and sends it to the Flask filtertube app. 

Then I as a parent get to at my leisure review the videos.  Any that I approve, are automatically downloaded and placed into a media folder that is available on my kids Plex accounts. 

### misc thoughts

- I like using the database as the intermediary between jobs, and I like using a separate request collecting and approving system from the downloading system.   This would allow for quick replacement of the downloading system if YouTube-DL became broken.
- I think there's a good chance I'll add a "approved channels" job that would look for videos in "Pending" state that are from particular channels that I trust and go ahead and auto-approve those. 

