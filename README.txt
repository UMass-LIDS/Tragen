TRAGEN is open-source software (tool) that generates synthetic request sequences that mimic the caching behavior of production request
traces from Akamai. TRAGEN comes equipped with footprint descriptors (FDs) obtained for various traffic classes such as video, web, downloads, etc.
that model the caching behavior of the traffic class. For a given user-specified traffic mix, TRAGEN uses the footprint descriptor calculus to compute
the FD that is representative of the traffic mix and then generates a request sequence from it. The code used to compute the FDs
is also made available for public use.


A. TRAGEN will be available to use in two forms:

1) GUI enabled
2) Command Line Interface

I. GUI enabled. 


II. Command Line Interface.

    Please type python3 ./tragen_cli.py -h to learn all the options.

B. TRAFFIC_MODELER code can be found in traffic_modeler.py. The traffic modeler
   is available only in the command line mode.

   Usage: python3 traffic_modeler.py -p <path_to_trace> -o <output_directory>

C. Downloading

   To download from git please use:

   git clone https://github.com/UMass-LIDS/Tragen.git

D. To cite TRAGEN, please use:
<link to IMC/ToN paper>











