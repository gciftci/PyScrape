"""---------------------------------------------------------------------------------------------------------
PyScrape: HTML-Parser
~~~~~~~~~~~~~~~~~~~~~

PyScrape parses webpages by HTML-Tags.
This module will be used in my web-scraper application

> Usage:
-> configure .env (or leave it empty for testing purposes with default values) and run

    >> .env-Variables:
    URL: Web-Page to parse                      e.g.: "https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index_aza.php?date=20230201&lang=de&mode=news"
    ENCAPSULATED_TAG: HTML-Tag to look for      e.g.: a

:Copyright: (c) 2023, Garbis Ciftci
:License: GNU GPL
    Copying and distribution of this file, with or without modification, are permitted in any medium 
    without royalty, provided the copyright notice and this notice are preserved. This file is offered 
    as-is, without any warranty.

---------------------------------------------------------------------------------------------------------"""
import os
import dotenv
import requests

DOTENV_CONFIG = dotenv.dotenv_values(".env")
WORKING_DIR   = os.path.dirname(os.path.realpath(__file__))

# ----------------------------------------------------------------------------------------------------------
# Defaults (change .env for customization)
URL                 = DOTENV_CONFIG["URL"]                          or      \
    "https://www.bger.ch/ext/eurospider/live/de/php/aza/http/index_aza.php?date=20230201&lang=de&mode=news"
ENCAPSULATED_TAG    = DOTENV_CONFIG["ENCAPSULATED_TAG"]             or      "a"
OUTPUT              = DOTENV_CONFIG["OUTPUT"]                       or      "console"
ACCEPTED_TAGS       = DOTENV_CONFIG["ACCEPTED_TAGS"].split(', ')
# ----------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------
# Globals
OUTPUTFILE    = WORKING_DIR + "\\" + DOTENV_CONFIG["OUTPUT_FILENAME"] + ".txt"
ALREADY_RUN   = False
TO_PRINT      = "NewSearch: \n"
TO_REPLACE    = {
        '\t'        :   '',         # Get rid of tabs
        '\n'      :   '',         # Get rid of unnecessary new-lines
        '  '        :   ' '         # Get rid of double-spaces
    }
# ----------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------
# Open Output-File if Output-Mode is set to "txt" and 
# file is not already open (shouldn't be, but just in case for w/e reason)
if OUTPUT == "txt" and not ALREADY_RUN:
    OUTPUTFILE_OBJ = open(OUTPUTFILE, "a")
    ALREADY_RUN = True
# ----------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------
# Tidy-up the response (replace stuff of HTTP_GET-content)
#
def parse_content(content):
    # Replace according to TO_REPLACE k/v
    for k, v in TO_REPLACE.items():
        while content.find(k) != -1:
            content = content.replace(k, v)
    return content.lower()

# ----------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------
# Scraping-Function
#
def scraper(URL, ENCAPSULATED_TAG):
    global TO_PRINT
    # Check TAG-input
    if ENCAPSULATED_TAG not in ACCEPTED_TAGS:
        print("ERROR Not supported Tag: " + ENCAPSULATED_TAG)
        raise SystemExit
    
    # Check URL-input
    if not URL and URL[0:4] != "http" and len(URL) < 7:
        print("ERROR No/Wrong URL: " + URL)
        raise SystemExit
    
    # If URL/TAG is fine -> init Tags/Counter
    TAG_OPEN = f"<{ENCAPSULATED_TAG}"           # Example, when ENCAPSULATED_TAG = a:
    TAG_CLOSE = f"</{ENCAPSULATED_TAG}"        #       _<a... </a>_
    start_index = 0

    # Try to reach URL or throw appriopriate exception
    try:
        get_response = requests.get(URL)
        # Status codes do not return an exception -> needs seperate check 
        # (btw: 200-299 is fine, actually, just accepting 200 atm)
        if get_response.status_code != 200:
            print(f"ERROR {get_response.status_code} ({get_response.reason}) -> \
                  {get_response.request.method}: {get_response.request.path_url}")
            raise SystemExit
        print(f"SUCCESS {get_response.status_code} ({get_response.reason}) -> \
              {get_response.request.method}: {get_response.request.path_url}")
        get_content = parse_content(get_response.content.decode(get_response.encoding))

        # search&find for TAGS [core]
        tmp_counter = 0
        while True:
            start_index = get_content.find(TAG_OPEN, start_index)
            if start_index == -1:       # find returns -1 if no matched, index throws error 
                break                   #(both usable though, any performance difference?)
            tmp_counter += 1
            end_index = get_content.find(TAG_CLOSE, start_index)
            get_match = get_content[start_index:end_index + len(TAG_CLOSE) + 1]
            start_index = end_index + len(TAG_CLOSE) + 1
            if OUTPUT == "console":
                print("#" + str(tmp_counter) + ": " + get_match)
            elif OUTPUT == "txt":
                TO_PRINT = TO_PRINT + get_match + "\n"
        if OUTPUT == "txt":
            OUTPUTFILE_OBJ.write(TO_PRINT)
            OUTPUTFILE_OBJ.close()    
    # ConnectionError
    except requests.exceptions.ConnectionError as e:
        print("ERROR ConnectionError: ", e)
        raise SystemExit
    # RequestException
    except requests.exceptions.RequestException as e:
        print("ERROR RequestException: ", e)
        raise SystemExit

scraper(URL, ENCAPSULATED_TAG)
