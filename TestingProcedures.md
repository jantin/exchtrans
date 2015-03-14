## Testing component, experiment, and session creation ##
  1. Go to http://exchtrans.homeip.net
  1. Click on the components tab.
  1. Create new components of each type. Note that negotiated exchange components integrate with widgets. So you need to have widget components built before you can add them to negotiated exchange components. Likewise, matcher components require negotiated exchange and reciprocal exchange components.
  1. Click on the experiment tab and make a new experiment. Add components to the experiment, reorder them (drag and drop) and save the experiment.
  1. click on the sessions tab and create a new session from the experiment you made in step 4.

## Testing experiment monitoring ##
  1. make an experiment with four text page components.
  1. make a new session with the text page experiment. After you make a new session you're dropped into the monitoring screen.
  1. go back to the sessions tab. Shift click on the join link. This will open a new window representing a participant. Go back to the first window and shift click the join link again to open a third window. You should now have three windows: two participant windows and one window showing you the sessions.
  1. in the sessions window, click on the link to monitor the text page experiment. You should see a column for each participant.
  1. Click on the start session link. The two participant windows should change after a few seconds to the first text page.
  1. advance the participant windows through the experiment. Each component the participant completes will be reflected in the monitoring screen. You do not need to refresh the monitoring screen. The status table is automatically updated every three seconds.

## Running experiments with a single PC ##
To simulate a running session with a single computer it is necessary to run multiple Firefox Instances. When a participant joins an experiment, exchtrans gives a cookies to the participant's browser. This cookies identifies the participant to the server. Each Firefox instance shares a single set of cookies. To start separate Firefox instances you use the command line to start Firefox's profile manager. Before you begin these steps, you should create an experiment.

The procedure for starting new instances of Firefox is slightly different for windows and Mac OS X.

If you're on windows, start the command line by clicking on Start and then Run. In the Run dialog box, enter the following:
```
"C:\Program Files\Mozilla Firefox\firefox.exe" -ProfileManager
```

If you're on Mac OS X, open the terminal (Applications > Utilities > Terminal) and enter the following:
```
/Applications/Firefox.app/Contents/MacOS/firefox -ProfileManager
```

  1. When you launch Firefox with one of the above commands, you will be presented with the Firefox Profile Manager. The first time you get to the profile manager, create 5 new profiles. (Mine are named Test1 ... Test5)
  1. Select your first new profile and click "Start Firefox". Point the instance to http://exchtrans.homeip.net and login. Use this instance to create a new session or monitor a session you already created. This instance represent the experimenter's station in the lab setting.
  1. Launch additional Firefox instances by executing the following from the command line: "C:\Program Files]Mozilla Firefox\firefox.exe" -P profileName -no-remote. For each additional instance you launch,replace "profileName" with the name of one of the testing profiles you created (e.g. Test1, Test2...). If you are testing an experiment with only two participants, you should launch two more instances, selecting the second and third profiles.
  1. Point all the additional instances to http://exchtrans.homeip.net and login with each instance.
  1. Click the "Join" link on the sessions tab with each participant instance. The monitor screen of the experimenter's instance will update with each player that joins.
  1. When all the participants have joined, go to the experimenter's instance and click on the start session link. (note: you will only be able to start the session if the number of joined players is within the range given on the experiment setup page.)
  1. Advance the participants through the experiment. The experimenter's monitoring screen will update to show the current component of each participant.

## Testing with multiple PCs ##
To use these directions you need 2 or 4 computers and preferably one person for each computer. The procedure for two players is described, but you could just as well try this with any even number of players. (Using an odd number of players would be experimental, but could work...theoretically)
  1. Have the person at PC-1 open up Firefox and some other browser (could be Internet Explorer, Opera, Camino, anything but firefox)
  1. Have the person at PC-2 open Firefox
  1. Point all the open browsers at http://exchtrans.homeip.net and login.
  1. Use the non-firefox browser on PC-1 to monitor the experiment
  1. Use the firefox browsers on each PC to join the experiment