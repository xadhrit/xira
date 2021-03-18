import json
import requests
from pprint import pprint
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from pyfiglet import Figlet
import sys
import time
import colorama

# checking python version

if sys.version > '3' :
    import urllib.parse as urlparse
    import urllib.parse as urllib 

else:
    import urllib.parse
    import urllib


try:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()

except:
    pass

G  = '\033[92m'
Y = '\033[93m'
B = '\033[94m'
R = '\033[91m'
W = '\033[0m'

def no_color():
    global G, B, Y, R, W
    G=R=B=Y=W=''

def banner():
    xb = Figlet(font='slant', justify='right' )
    print(xb.renderText('XIRA'))
    print( G + " Coded by Adhrit.  github.com/imadhrit ")
banner()


def get_all_forms(url):
    """Given a `url` , it returns all forms from the HTML content  """
    soup = bs(requests.get(url).content, "html.parser")
    return soup.find_all("form")


def get_form_details(form):

    """
    This function extracts all possible useful information about an HTML `form`
    """
    details = {}

    # get the form action (target url)
    action = form.attrs.get("action").lower()

    #get the form method (POST, GET, etc.)
    method = form.attrs.get("method", "get").lower()

    # get all input details such as type and name
    inputs = []

    for input_tag in form.find_all("input") :
        payload_type = input_tag.attrs.get("type", "text")
        payload_name = input_tag.attrs.get("name")
        inputs.append({"type": payload_type,"name": payload_name})

    #put everything to the resulting dictionary
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details

def submit_form(form_details, url, value):
   
    # Construct the full URL (if the url provided in action in relative)
    target_url = urljoin(url, form_details["action"])

    # get the input fields
    time.sleep(2)
    inputs = form_details["inputs"]
    data = {}

    for input in inputs:
        # replace all text and search values with `value`

        if input["type"] == "text" or input["type"] == "search":
            input["value"] = value

        payload_name = input.get("name")
        payload_value = input.get("value")
        if payload_name and payload_value :
            # if payload name and value are not None,
            # then add them to the data of form submission
            data[payload_name] = payload_value

    if form_details["method"] == "post":
        return requests.post(target_url, data=data)
    else:
        return requests.get(target_url, params=data)


def xira(url):

    #get all forms from the URL
    forms = get_all_forms(url)
    print( '%s [+] Detected on %s forms on %s%s'%(R,len(forms), url ,Y ) )
    if (len(forms)==0):
        print("Thus , we don't get any input form here. We are going out now! " )
    else:
        with open ('payload.json','r', encoding="utf-8") as file:
            payload_data = json.load(file)

            file.close()
            try:
                is_vulnerable = False
                for form in forms:
                    form_details = get_form_details(form)

                    for payload_name in payload_data.values():
                        print("Going through each payload : " )
                        for payload in payload_name:

                            for payload_name in payload.values():

                                payload_name = str(payload_name)


                                content = submit_form(form_details,url,payload_name).content.decode()
                                if payload_name in content:

                                   print("%s [+] XSS Detected on %s%s" %( G, Y, W))
                                   print("%s [*] Form Details: %s%s" %(Y,B,R) )
                                   pprint(form_details)
                                   print("%s  Successful Payload : %s"%( G ,payload_name))
                                   is_vulnerable = True
                                else:
                                   print("%s No XSS Found, WE LOSE HERE! " %(R) )

                return is_vulnerable

            except Exception as error:
                print (error)
                pass




if __name__ == '__main__':
    url = input( "%s Enter Target : " %(B) )
    print(xira(url))
     



