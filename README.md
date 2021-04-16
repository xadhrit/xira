## XIRA : xss vulnerablity scanner 

<p align=center>
<img src="xira.png"  height="450px" width="800px" alt="xira" />
</p>


### Installation

```console
# clone the repo
$ git clone https://github.com/xadhrit/xira.git

# change the working directory to xira
$ cd xira

# install the requirements
 
For Linux
$ python3 -m pip install -r requirements.txt

For windows
> python -m pip install -r requirements.txt
```

### Usage

```console
FOR LINUX/WINDOWS

$ python3/python xira.py

Enter the target's url : https://www.example.com
```

<p align=center>
<img src="ss1.png"  height="450px" width="800px" alt="xira" />
</p>



### Results

```console

$ All details with successful payloads.
$ True
```

<p align=center>
<img src="ss.png"  height="450px" width="800px" alt="xira" />
</p>

### Payloads Template
We can use payload_template.json to use payloads from Seclists or wherever you want. final.json will be our new payload.json file for using in our XSS Scanning.
```bash
while read line; do cat payload_template.json | jq --arg value "$line" '.payload[]|=.+{ "payload_name" : $value }' >> final.json;done < XSS-Jhaddix.txt
```

##### Payloads :

```console

clone the repo : git clone https://github.com/xadhrit/xss-hacker.git

```
###### Issues:
Contact me : <a href= "https://twitter.com/xadhrit">Twitter</a>
           

