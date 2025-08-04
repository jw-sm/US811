<div align="center">

  <picture>
    <source media="(prefers-color-scheme: light)" srcset="/docs/811_logo_light.svg">
    <img src="/docs/811_logo_light.svg" width="50%" height="50%" alt="811 Logo">
  </picture>

  <h3>
    An automation tool for surveying, profiling, and submitting Pole Restoration/Pole Installation work for US811
  </h3>
</div>

<p><strong>Core Logic for Pole Restoration:</strong></p>
<ul>
    <li>[x] parse csv file containing 3 columns, into typeddict
    <li>[ ] login automation to avoid getting the account disabled</li>
    <li>[ ] given a gps coords, find the nearest street it belongs to
    <li>[ ] given a street name/wayid/streetid, find the nearest intersection
    <li>[ ] given a gps coords, get measure the distance in feet following the road from inter to gps perpendicular to nearest street 
    <li>[ ] measure the distance in feet of the gps coordinates perpendiculat to the nearest street
    <li>[ ] incorporate a the standard verbiage of the company for each state
    <li>[ ] reverse engineer each 811 state identify business flows and find api that submits the ticket
</ul>

<p><strong>Unit testing:</strong></p>
<ul>
    <li>[ ] helpers.py
    <li>[ ] streets.py
</ul>

<p><strong>Upcoming features:</strong></p>
<ul>
    <li>[ ] automatic login to all US811 states to avoid account deactivation
    <li>[ ] csv file vlookup???
    <li>[ ]  
</ul>


<p><strong>Refactoring the core logic</strong></p>
<ul>
    <li>[ ] File and logic cleanup 
 
</ul>






