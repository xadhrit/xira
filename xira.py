"""
Date : 22-April-2021
Author: adhrit
Github: https://github.com/imadhrit
Description: Xira is a cross-site scripting vulnerablity scanner.
Code Flow : First Collect all the forms from website then put payloads in input fields and display form and payload.
Contributor: @naivenom

Build CSRF Token in hidden inputs and Cookie POST Requests. Use pattern hidden inputs, and include type email. Also include textarea, common in Contact Us Forms.
Implemented Stored XSS functionality.
Basic XSS detection according to HTML tags inyected in responses.
"""
import sys, getopt
import colorama
import requests
import time
from pprint import pprint
from bs4 import BeautifulSoup as bs 
from urllib.parse import urljoin
import json
from payload import PayloadsInfo
from pyfiglet import Figlet
import re

# Checking python version
if sys.version > '3':
    import urllib.parse as urlparse
    import urllib.parse as urllib

else:
    import urlparse
    import urllib

#In case you cannot install some of required development packages
# there's also an option to disable the Warnings

try:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()

except:
    pass
#Check if we are running on windows os
# Declare color variables with colorama
""" FOR WINDOWS
is_wind = sys.platform.startswith('win')

if is_wind:
    # Windows deserves coloring too :D
    G = '\033[92m'  # green
    Y = '\033[93m'  # yellow
    B = '\033[94m'  # blue
    R = '\033[91m'  # red
    W = '\033[0m'   # white
    try:
        import win_unicode_console , colorama
        win_unicode_console.enable()
        colorama.init()
        #Now the unicode will work ^_^
    except:
        print("[!] Error: Coloring libraries not installed, no coloring will be used")
        G = Y = B = R = W = G = Y = B = R = W = ''


else:
    G = '\033[92m'  # green
    Y = '\033[93m'  # yellow
    B = '\033[94m'  # blue
    R = '\033[91m'  # red
    W = '\033[0m'   # white
""" 
G = '\033[92m'  # green
Y = '\033[93m'  # yellow
B = '\033[94m'  # blue
R = '\033[91m'  # red
W = '\033[0m'   # white

def no_color():
   global G,B,Y,R,W
   G=B=R=Y=W=''

def banner():
    xira_banner = Figlet(justify='right')
    xb = Figlet(font='slant', justify='right' )
    print(  G + xb.renderText('XIRA'))
    print( R + "                                   ~#  Coded by Adhrit.  twitter -- @xadhrit ")
    print( W + "                                   ~#  Contributor: Naivenom.  twitter -- @naivenom ")
banner()

def custom_cookie(url):
    res = requests.get(url)
    soup = bs(res.content, "html.parser")
    if res.cookies:
        for cookie in res.cookies:
            cookie = input("Enter cookie : ")
            print("Cookie Session = "+ cookie)
        cookies = {cookie}
        return soup.find_all("form"), cookies
    return [soup.find_all("form")]

def get_all_forms(url):
    """Given a `url` , it returns all forms from the HTML content  """
   
    response = requests.get(url)
    soup = bs(response.content, "html.parser")
    if response.cookies:
        for cookie in response.cookies:
            print("Cookie Session= "+ cookie.value)
        cookies = {cookie.name: cookie.value}
        return soup.find_all("form"),cookies
    return [soup.find_all("form")]

def get_all_payloads():
    """Get all payloads from PayloadsInfo class object  
        
    """ 
    return PayloadsInfo('payload.json')

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

    for input_tag in form.find_all("input"):
        payload_value=""
        payload_type = input_tag.attrs.get("type")
        payload_name = input_tag.attrs.get("name")
        payload_pattern = input_tag.attrs.get("pattern")
        if input_tag.attrs.get("pattern"):
            pattern = payload_pattern
        else:
            pattern = None
        if input_tag.attrs.get("type") == "hidden": #build valid common names of csrf protections. This check is just for valid hidden inputs
            if input_tag.attrs.get("value"):
                payload_value = input_tag.attrs.get("value")
        inputs.append({"type": payload_type,"name": payload_name,"value":payload_value,"pattern":pattern})
    pattern = None #Just needed pass into
    for input_tag in form.find_all("textarea"): #Type tag doesn't exist, so hardcoded is needed.
        payload_name = input_tag.attrs.get("name")
        inputs.append({"type": "textarea", "name": payload_name, "value":payload_value, "pattern":pattern})
    #put everything to the resulting dictionary
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    #print(details)
    return details

def submit_form(form_details, url, value, cookies):
    """Submits a form given in `form details`
     
     Params:
          form_details (list): a dictionary that contian form information
          url (str) :  the original URL that contain that form
          value (str) : this will be replaced to all text and search inputs

     Returns the HTTP Response after from submission

    """
    # Construct the full URL (if the url provided in action in relative)
    target_url = urljoin(url, form_details["action"]) #idx of tuple
    
    # get the input fields
    
    inputs = form_details["inputs"]
    data = {}
    #print(inputs)
    for input in inputs:
        # replace all text and search values with `value`
        if input["type"] == "text" or input["type"] == "search" or input["type"] == "email" or input["type"] == "textarea":
            input["value"] = value
            if input["type"] == "email":
                input["value"] = "some@blabla.com"
            #print(input['pattern'])
            if input['pattern']:
                input["value"] = "http://evil.com"
        payload_name = input.get("name")
        payload_value = input.get("value")
        if payload_name and payload_value :
            # if payload name and value are not None,
            # then add them to the data of form submission
            data[payload_name] = payload_value
    #print(data)
    if form_details["method"] == "post":
        if cookies:
            return requests.post(target_url, data=data, cookies=cookies)
        else:
            return requests.post(target_url, data=data)
    else:
        if cookies:
            return requests.get(target_url, params=data, cookies=cookies)
        else:
            return requests.get(target_url, params=data)

#main xira function
def xira(url):
    
    """
     Given a `url` , it prints all XSS vulnerable forms and returns True if any is vulnerable, False Otherwise
     >> If target website doesn't contain any  form:
        return exit, None
     >> else:
             >> open the payload file 
             >> go through each form's input field
             >> with each payload
             >> if find XSS :
                      return  True, form details
             >> else:
                      return  False (default)      
    """ 
    #get all forms from the URL
    #forms = custom_cookie(url)
    forms = get_all_forms(url)
    redirect = False
    #print(forms[0])
    if (len(forms) == 2): #Just take into account Cookie 
        cookie = forms[1]
    else:
        cookie = None
    print( '%s [+] Detected %s forms on %s%s'%(R,len(forms[0]), url ,Y ) ) 
    if (len(forms[0])==0):
        print("Thus , we don't get any input form here. We are going out now! " )
    else:
        with open ('payload.json','r', encoding="utf-8") as file:
             payload_data = json.load(file)
             file.close()
             try:
                 is_vulnerable = False
                 for form in forms[0]:
                     form_details = get_form_details(form)
                     print(form_details)
                     
                     for payload_name in payload_data.values():
                         print("Going through each payload : " )
                         for payload in payload_name: 
                             for payload_name in payload.values(): 
                                payload_name = str(payload_name)
                                #print("PAYLOAD ->> ",payload_name)

                                content_raw = submit_form(form_details,url,payload_name,cookie)
                                if content_raw.history:
                                    #Its common that Contact Form have redirections, so take account that and check for stored o reflected in main URI
                                    if str(content_raw.history[0])[11:14] == "302":
                                        redirect = True
                                content = submit_form(form_details,url,payload_name,cookie).content.decode()
                                
                                soup = bs(content, "html.parser")
                                elem = [soup.get_text()]
                             
                                matches = [match for match in elem if payload_name in match]
                                #print(matches) # If match, we confirm our payload within html tags, as data. 

                                xss_attr = None
                                for tag in soup.find_all(re.compile("^i")): #Just checking for XSS reflected into attribute with angle brackets HTML-encoded
                                    xss_attr = [match for match in tag.attrs if "on" in match] #on* events
                                    
                                if redirect:
                                    check_stored = requests.get(url) #Just check for XSS Stored
                                    redirect = False
                                    soup = bs(check_stored.text, "html.parser")
                                    if payload_name in check_stored.text:
                                        print("%s [+] Input Stored triggered on %s%s" %( G, Y, url))
                                        print("%s [*] Form Details: %s%s" %(Y,B,R) )
                                        pprint(form_details)
                                        
                                        print("%s  Successful Payload : %s"%( G ,payload_name))
                                        is_vulnerable = True
                                    else:
                                        print("%s No Input Stored triggered. " %(R) )
                                if xss_attr:
                                    print("%s [+] XSS Detected on %s%s" %( G, Y, url))
                                    print("%s [*] Form Details: %s%s" %(Y,B,R) )
                                    pprint(form_details)

                                if matches:
                                    print("%s No XSS Found, WE LOSE HERE! " %(R) )
                                elif payload_name in content:

                                   print("%s [+] XSS Detected on %s%s" %( G, Y, url))
                                   print("%s [*] Form Details: %s%s" %(Y,B,R) )
                                   pprint(form_details)

                                   print("%s  Successful Payload : %s"%( G ,payload_name))
                                   is_vulnerable = True
                                else:
                                   print("%s No XSS Found, WE LOSE HERE! " %(R) )
                                
                                
                 return is_vulnerable
             except KeyboardInterrupt as key:
                 print(key)
                 pass
            
             except Exception as error:
                  print (error)
                  pass
     
         
if __name__ == '__main__':
    try:
      opts, args = getopt.getopt(sys.argv[1:],"hu:",["url="])
    except getopt.GetoptError:
        print('xira.py -u <url>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('xira.py -u <url>')
            print('xira.py -c <cookie> -u <url>')
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg
            print(xira(url))
        elif opt in ("-c", "--cookie", "-u", "--url"):
            cookie = arg
            print(xira(url))      
