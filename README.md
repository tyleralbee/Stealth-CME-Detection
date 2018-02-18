


**Title**: Stealth CME Detection 

**Team members**: Tyler Albee, Shawn Polson

**Description**: Working with data from CU Boulder's SDO EVE instrument, which comes in the form of fitts files. The team intends to help with the detection and characterization of stealth CMEs. Working under James Mason from Goddard, a NASA Postdoctoral Program Fellow. 

**Prior Work**: 
 - "Solar Eruptive Events: Coronal Dimming and a New CubeSat Mission" - Ph.D dissertation by James Paul Mason, University of Colorado at Boulder (https://scholar.colorado.edu/asen_gradetds/157/)
 - SOHO LASCO CME [catalog](https://cdaw.gsfc.nasa.gov/CME_list/UNIVERSAL/2010_05/univ2010_05.html)

**Datasets**: 
 - SDO EVE telemetry 
 - Provided by LASP (Laboratory for Atmospheric and Space Physics at CU)
 - http://lasp.colorado.edu/home/eve/data/data-access/
 - We have downloaded chunks, but not all of it yet.
 - Shawn works at LASP, so he has permenent access to this data

**Proposed work**: what do you need to do?

**Data cleaning**: 
 - The MEGS-B spectrograph has limited exposure of about 3 hours per day normally to prevent rapid degradation of the detector, so we'll clean out the null values.

**Data preprocessing**: 
 - Spectral measurements span 6-105 nm up to May 26, 2014 when the MEGS-A spectrograph had a power anomaly and was permanently decommissioned. After that, spectral measurements only span 33-105 nm. 

**Data integration**:

etc.

**List of tool(s) we intend to use**:
 - Python (savReaderWriter, pandas)
 - IDL
 - LaTiS (a software framework for data access, processing, and output created and maintained by the Web Team at LASP--it uses a "functional data model" and Shawn helps develop it)

Evaluation: How you can evaluate your results 
