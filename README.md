## TRAGEN

TRAGEN is a tool that produces synthetic traces that have similar caching properties as the original traces in the sense that the two traces will have the same hitrates in a cache simulation. TRAGEN is seeded with realistic footprint descriptor models [[1]](#1) computed from original traces from Akamai's production CDNs that models the caching properties of the original traces. Using the footprint descriptors, TRAGEN produces a synthetic trace that fits the model.

## 1. Installation

1. TRAGEN requires the installation of [python3](https://www.python.org/downloads/).

2. TRAGEN requires the following packages to be installed - numpy, scipy, pyQt5 and datetime.
   * ``` pip3 install numpy, scipy, pyQt5, datetime ```

## 2. Synthetic trace generation

User can select a traffic model from the [available traffic models](#available-traffic-models) to produce a synthetic trace that fits the model.

1. The user can select a model that is described as Mix to generate a synthetic trace that is representative of the original trace obtained from a server that is serving a mix of traffic classes.

2. Or, the user can select multiple traffic models and provide the required traffic volumes for each selected option to create his/her own traffic mix. For e.g., 10Gbps of traffic from Amazon mixed with 5Gbps of traffic from Microsoft.

We provide the option of using a GUI or a command line interface.

### 2.1. GUI

Run the following command in the home directory of TRAGEN to operate in the GUI mode.
   * ``` python3 tragen_gui.py ```

You would see the following GUI. 

![GUI](images/TRAGEN_2.png)

1. **Select hit rate type**. Select if the synthetic trace is to have the same Request hit rate or Byte hit rate as the original.
2. **Enter trace length**. Specify the number of requests in the synthetic trace.
3. **Select traffic volume unit**. Select if the traffic volume field in the third column of the table will be input as requests/second or Gigabits per second (Gbps).
4. **Select required traffic classes and specify the traffic volume**. Select traffic classes from the first column of the table and specify a traffic volume for the selected traffic classes in the third column of the table. The second column provides a description of each choice. Each choice is either a pure traffic class  such as video, web, or social media traffic class. Or, it is a traffic mix itself.
5. **Generate**. Hit the generate button and TRAGEN will start producing the synthetic trace.

The produced synthetic trace is found in the directory ./OUTPUT/

### 2.2. Command line interface (CLI)

Run the following command in the home directory of TRAGEN to operate in the CLI mode.
   * ``` python3 tragen_cli.py -c <config_file> -d <output_directory> ```

#### 2.2.1. Config file

The config file is to be in the json format. An example of a config file is:

```json
{
    "Trace_length": "100000000",
    "Hitrate_type": "bhr",
    "Input_unit"  : "reqs/s",
    "Traffic_classes" : [
        {
            "traffic_class": "v",
            "traffic_volume": "1000"
        },
        {
            "traffic_class":"w",
            "traffic_volume":"2000"
        }
    ]
}
```

1. **Trace_length**. Specify the number of requests in the synthetic trace.
2. **Hitrate_type**. Enter rhr or bhr if the synthetic trace is to have Request hit rate or Byte hit rate, respectively, as the original.
3. **Input_unit**. Enter the unit with which the traffic volume for each traffic class will be specified - reqs/s or Gbps.
4. **Traffic_classes**. A map of traffic_class and its respective traffic volume. 
   * traffic_class should be one of the traffic classes specified in the [available traffic models](#available-traffic-models).
   * traffic_volume field specifies the traffic volume for the traffic class.

#### 2.2.2. Output

The produced synthetic trace is in the specified <output_directory>.

## 3. Generate and submit traffic models

#### 3.1 Generate traffic models

Users can generate footprint descriptor traffic models and object size distribution from their own original traces. The original trace should be in file with each request on a new line. Each request is comma seperated list of timestamp, object_id, object_size. For example,

```
1532702631,0,26624
1532702631,1,12288
1532702631,2,26624
1532702631,3,26624
	.
	.
	.
	.
```

To generate a footprint descriptor model use the following command,
   * ``` python3 traffic_modeler.py <path_to_original_trace> <output_dir>```
   
The output_dir contains the footprint descriptor and the byte-weighted footprint descriptors for the specified trace.

#### 3.2. Submitting traffic models

Consider adding your footprint descriptors to our repository. To do so,

1. Create a directory FOOTPRINT_DESCRIPTOR/<your_traffic_class_name>.
2. Copy the footprint descriptor (named as fd.txt), byte-weighted footprint descriptor (named as bfd.txt) and the object size distribution (sz.txt) to FOOTPRINT_DESCRIPTOR/<your_traffic_class_name>/.
3. Create an entry in [available traffic models](#available-traffic-models).
4. Update the file FOOTPRINT_DESCRIPTOR/available_fds.txt

## 4. Developer mode.

We welcome users to suggest modifications to improve the quality of the code or add new features to the existing codebase. Use the developer branch to make edits and submit a change.


## 5. Available traffic models

The currently available traffic models are:

| |Traffic class|                        Description| Gbps | Reqs/s| Traffic type|
|:-|:-:|:-------------------------------------------------------------|:-:|:-:|:--:|
|1|V|Traffic collected from servers predominantly serving video traffic|1.5|400.2|Video|
|2|W|Traffic collected from servers predominantly serving web traffic|2.29|5860|Web|
|3|EU|Traffic collected from a cluster of servers serving a mix of traffic|1.31|403|Mix|
|4|TC|Traffic collected from a cluster of servers serving a mix of traffic|0.36|820|Mix|
|5|EU-0|Subset of eu trace corresponding to media traffic|0.012|20.64|SocialMedia|
|6|EU-1|Subset of eu trace corresponding to media traffic|0.48|70.44|SocialMedia|
|8|EU-3|Subset of eu trace corresponding to media traffic|0.036|59.2|SocialMedia|
|10|EU-5|Subset of eu trace corresponding to media traffic|0.434|42.82|SocialMedia|
|11|EU-6|Subset of eu trace corresponding to media traffic|0.026|23.55|SocialMedia|
|12|EU-7|Subset of eu trace corresponding to media traffic|0.00086|24|Web|
|13|EU-8|Subset of eu trace corresponding to media traffic|0.027|82.74|SocialMedia|
|14|EU-9|Subset of eu trace corresponding to media traffic|0.756|5.38|Web|
|15|EU-0|Subset of tc trace that corresponds to downloads|70|22.9|Download|
|15|EU-1|Subset of tc trace that corresponds to images|8|243|Images|
|16|EU-2|Subset of tc trace that corresponds to media|40|141|Media|
|17|EU-3|Subset of tc trace that corresponds to web|250|406|Web|

## 6. Citation

Please cite the following publication on using TRAGEN for your work.

TRAGEN: A Synthetic Trace Generator for Realistic Cache Simulations.
In ACM Internet Measurement Conference (IMC ’21), November 2–4, 2021, Virtual Event, USA. ACM,New York, NY, USA, 14 pages, https://doi.org/10.1145/3487552.3487845

## 7. References

<a id="1">[1]</a> 
Sundarrajan, Aditya, Mingdong Feng, Mangesh Kasbekar, and Ramesh K. Sitaraman. "Footprint descriptors: Theory and practice of cache provisioning in a global cdn." In Proceedings of the 13th International Conference on emerging Networking EXperiments and Technologies, pp. 55-67. 2017.

## 8. Acknowledgements
This work was supported in part by NSF grants CNS-1763617 and CNS-1901137.
