TRAGEN is open-source software (tool) that generates synthetic request sequences that mimic the caching behavior of production request
traces from Akamai. TRAGEN comes equipped with footprint descriptors (FDs) obtained for various traffic classes such as video, web, downloads, etc.
that model the caching behavior of the traffic class. For a given user-specified traffic mix, TRAGEN uses the footprint descriptor calculus to compute
the FD that is representative of the traffic mix and then generates a request sequence from it. The code used to compute the FDs
is also made available for public use.

Information about the available footprint descriptors can be found in the file FOOTPRINT_DESCRIPTORS/available_fds.txt.
There are two types of footprint descriptors available.
- The first type is computed from a server that is serving a mix of traffic.These footprint descriptors are marked as - "Mix".
Users who would like to test their caching algorithm/system with a trace that resembles a production traffic mix,
can select these footprint descriptors as input.
- The other type of footprint descriptors could correspond to individual traffic classes such as video, images, web, social media etc.
and are marked by their respective traffic classes. Users can mix and match the traffic classes and also provide the traffic volume for each
traffic class in the mix as the input. For example, a user can specify the traffic mix such as 10 Gbps of video traffic from Amazon mixed
with 5 Gbps of download traffic from Microsoft.

The columns in the file FOOTPRINT_DESCRIPTORS/available_fds.txt are:
Serial number, Footprint descriptor name, Traffic class, Request rate, Byte rate.


A. TRAGEN will be available to use in two forms:

1) GUI enabled
2) Command Line Interface

I. GUI enabled.

<insert figure with labels>

Step 1. Enter the required hitrate type. Selecting <Request-hitrate> will generate a sequence
        with the same request-hitrate curves as the original. Selecting <Byte-hitrate> will generate
	a sequence with the same byte-hitrate curves.

Step 2. Enter the required length for the trace to be generated.

Step 3. Select the required traffic classes to be mixed.

Step 4. The original request-rate (or the byte-rate) for the traffic class is provided in column 3.
     	Modify to any value. Please press <Enter>, once you enter a value

Step 5. Press Go! and the progress can be monitored on the progress bar.

Step 6. Navigate to directory OUTPUT/<curr_time> to find generated_sequence.txt


II. Command Line Interface.

    Please type python3 ./tragen_cli.py -h to learn all the options.

B. TRAFFIC_MODELER code can be found in traffic_modeler.py. The traffic modeler
   is available only in the command line mode.

   Usage: python3 traffic_modeler.py -p <path_to_trace> -o <output_directory>

C. Downloading

   To download from git please use:

   git clone https://github.com/UMass-LIDS/tragen.git

D. To cite TRAGEN, please use:
<link to IMC/ToN paper>











