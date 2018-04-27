# Stealth CME Detection

## Team members: 
 - Tyler Albee 
 - Shawn Polson

## Description: 
Working with data from LASP's SDO EVE instrument, which comes in the form of .fits files, the team helped with the detection and characterization of stealth CMEs. We worked under James Mason, a Postdoctoral Program Fellow at NASA's Goddard Spaceflight Center, and Don Woodraska, a professional researcher at LASP. 

In short, this project aimed to create the first ever catalog of stealth CMEs by cataloging coronal dimming events in the SDO EVE data. We were seeking to answer questions like “What proportion of our sun’s CMEs are stealth CMEs?” “How can stealth CMEs be characterized by their dimming profiles?” and “What is the risk of a stealth CME damaging Earth’s technology?” 

The key result of our work is our estimation of what percentage of the Sun’s CMEs are stealth CMEs. We estimate that somewhere around 32.1% of them are stealth CMEs. We were not successful in characterizing these stealth CMEs in terms of their dimming depth, duration, and slope, which was one of our main goals. But we have written a collection of Python routines here that would do just that, if given enough time to run. Also, contained inside the `Labeled SOHO Catalog` folder is a copy of the SOHO catalog of CMEs (maintained by the European Space Agency and NASA at the CDAW Data Center) with an added column to it: *"Stealth?"* That data set is our best estimation for which of the Sun's CMEs are stealth CMEs. Because we were not as successful as we had hoped, the biggest application of our work will be letting scientists at LASP (and James Mason at Goddard) study the potential stealth CMEs we have labeled. Scientists have been using the SOHO catalog of CMEs since the 1990s, but the catalog has notably never had that *“Stealth?”* column. Our SMEs tell us that everyone wants it, and our work moved that desire one step closer to reality. We cannot speak about direct applications of our work, because there are not many. But we can speak about the benefits of understanding this solar activity in general. CMEs are a class of phenomena that, while not often thought about, could potentially end modern society as we know it. If a powerful enough CME were pointed at Earth, it could fry electronics at a global scale, and the consequences of that hardly need explaining. Stealth CMEs, by nature, are not preceded by any obvious solar activity and they therefore happen out of nowhere. They are typically smaller in magnitude, but the risk of Earth being surprised by a nasty stealth CME is currently unknown. And since humans are fortunate enough to have a space program, we should dedicate some effort towards understanding that risk—as we did here.



### Prior Work: 
 - "Solar Eruptive Events: Coronal Dimming and a New CubeSat Mission" - Ph.D dissertation by James Paul Mason, University of Colorado at Boulder (https://scholar.colorado.edu/asen_gradetds/157/)
 - SOHO LASCO CME [catalog](https://cdaw.gsfc.nasa.gov/CME_list/)

## TODO: Link to the video demonstration
11_StealthCMEDetection_Part5.(extension)

## Link to our final project paper:
https://github.com/tyleralbee/Stealth-CME-Detection/blob/master/11_StealthCMEDetection_Part4.pdf
