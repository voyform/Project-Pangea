==================================================================================
				PROJECT PANGEA
==================================================================================

Project Pangea is an open-source application written in Python under the MIT License 
for any gmail user that may want to increase their security by using Pangea URLIntel
to scan malicious links.

The tool analyzes email messages on user's gmail account, recognizes any links in the
body of the message and allows to scan found URLs, as well as any other URL the user
wants to investigate. 

Project Pangea is avaialble from:
https://github.com/voyform/Project-Pangea/tree/main/Source%20code


The application is available as an .exe file, however it is also possible to run
the software as a python script after downlaoding all the necessary files 
and dependancies.  				
___________________________________________________________________________________

				CONFIGURATION

You will need to download Google Authentication modules for python:
>>> pip install --upgrade google-auth 
>>> pip install google-auth-oauthlib 
>>> pip install google-auth-httplib2
>>> pip install --upgrade google-api-python-client

To use the software to its full extent, it is required to have a pangea API key
(found on pangea.cloud) and Gmail developer API enabled (with authentication files
downloaded). 

The location of the gmail credentials file path, as well as the Pangea API key have
to be included in the configuration file in this format:

api_key='<your_api_key>'
credentials_file_path='<path_to_file>'

___________________________________________________________________________________

				USING THE APP

How to use the application:

1. Make sure you have your pangea API key enabled for URLIntel and your credentials
file for the Gmail API.

2. Download the source code folder from the github repository.

3. In the configuration file, set api_key='<your_api_key>' 
and credentials_file_path='<path_to_file>'.

4. Run GUI.py.

5. You will be presented with a list of email subjects found on your inbox, 
as well as a URL scan bar. 

5.1. To use the scan bar, you may input any url starting with 'http' or 'https'
and press the "Scan URL" button.

5.2. To scan your emails, click on any chosen email found in the list. You will be
presented with more information about the email, as well as an option to scan any 
links found in the content (if any were found). 

6. If the list displays outdated emails, you always have the option to use "Refresh"
button, wich will refresh the list to display latest emails.   




This application was developed as an entry for pangea Securathon Showdown 2024.

For any information or requests contact: 

author: Wojciech Sołtys

email: wojciech.soltys0 at gmail.com
