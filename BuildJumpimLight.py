##################################################################
#             Jumpim apps Build script for Ragnarokkr            #
#                         HOSTEUR 2021                           #
#                                                     Florent G. #
##################################################################²

import requests
import json
import random
import os

# Randomise number ans use it to create unique env name
rndid = random.randint(1111,9999)

# Set variables for authentication and host Ragnarokkr API
# User Token
session=os.environ["RAG_TK"]
# Fixed Provider ID
appid="1dd8d191d38fff45e62564fcf67fdcd6"
# Fixed Provider API HOST
HosteurRagHost="https://app.rag-control.hosteur.com"

# Base Env Name and DisplayName
envname = "jmp-light-" + str(rndid)
envdisp = "Jumpim Light " + str(rndid)

# Fixed Source Repository Name on Deployement Manager
gitsrcreponame="Jumpim-Test"
# Fixed Repo based URL for conf and scripts
gitsysbaseurl="https://raw.githubusercontent.com/FlorentHosteur/jmpsys/main"

# Variables to SET
nodeid = ""
gitsrcrepoid = ""

# Node Params
fixedcloudlet="1"
dynamiccloudletmax="6"
phpversion="php8.0"
region="thor"
# Define empty payload and same headers for all requests.
payload={}
headers = {
  'Content-Type': 'application/json',
}


# Parse Deployment Manager to get correct Git Repository
url = HosteurRagHost + "/1.0/environment/deployment/rest/getrepos?session=" + session + "&appid=" + appid

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text) #debug

repos=response.json()["array"]
for rp in repos:
      if rp["name"] == gitsrcreponame:
          gitsrcrepoid = str(rp["id"])
          break

# Create New node from Apache2 template with php 8.0 (last)
url = HosteurRagHost + "/1.0/environment/control/rest/createenvironment?nodes=[{\"displayName\":\"jumpim-light-app\",\"extip\":\"false\",\"fixedCloudlets\":\"" + fixedcloudlet + "\",\"flexibleCloudlets\":\"" + dynamiccloudletmax + "\",\"nodeType\":\"apache2\"}]&session=" + session + "&appid=" + appid + "&env={\"displayName\":\"" + envdisp + "\",\"diskLimit\":\"30000\",\"engine\":\"" + phpversion + "\",\"region\":\"" + region + "\",\"shortdomain\":\""+ envname +"\",\"sslstate\":\"true\"}"

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text) #debug

# Get created node ID
nodeid=response.json()["response"]["nodes"][0]["id"]

# Deploy Source from Git Repo on apache node docroot /var/www/webroot/ROOT added before on Deployment Manager
url = HosteurRagHost + "/1.0/environment/deployment/rest/deploy?session=" + session + "&appid=" + appid + "&envName="+ envname +"&nodeGroup=cp&repo={\"id\":" + gitsrcrepoid + ",\"branch\":\"master\"}&settings={\"autoUpdate\":true,\"autoUpdateInterval\":1,\"autoResolveConflict\":true,\"zdt\":false}&hooks={\"preDeploy\":\"\",\"postDeploy\":\"\"}&context=ROOT"

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text) #debug

# Start Composer Install
url = HosteurRagHost + "/1.0/environment/control/rest/execcmdbyid?session=" + session + "&appid=" + appid + "&envName=" + envname + "&nodeId="+ str(nodeid) +"&commandList=[{\"command\": \"curl -s "+ gitsysbaseurl + "/ressources/scripts/composer.sh | bash\"}]"

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text) #debug

# Upload ressouces file
# Create Folder to upload ressources files
url = HosteurRagHost + "/1.0/environment/control/rest/execcmdbyid?session=" + session + "&appid=" + appid + "&envName=" + envname + "&nodeId="+ str(nodeid) +"&commandList=[{\"command\": \"mkdir -p /var/www/jmpres\"}]"

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text) #debug

#  - php.ini (upload from Git repos url)
url = HosteurRagHost + "/1.0/environment/file/rest/upload?session=" + session + "&appid=" + appid + "&envName=" + envname + "&nodeId="+ str(nodeid) +"&sourcePath="+ gitsysbaseurl + "/ressources/conf/php.ini&destPath=/var/www/jmpres/php.ini&overwrite=true"

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text) #debug

## Copie uploaded file to main file (because of rights)
url = HosteurRagHost + "/1.0/environment/control/rest/execcmdbyid?session=" + session + "&appid=" + appid + "&envName=" + envname + "&nodeId="+ str(nodeid) +"&commandList=[{\"command\": \"cat /var/www/jmpres/php.ini > /etc/php.ini\"}]"

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text) #debug

#  - httpd.conf (upload from Git repos url)
url = HosteurRagHost + "/1.0/environment/file/rest/upload?session=" + session + "&appid=" + appid + "&envName=" + envname + "&nodeId="+ str(nodeid) +"&sourcePath="+ gitsysbaseurl + "/ressources/conf/httpd.conf&destPath=/var/www/jmpres/httpd.conf&overwrite=true"

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text) #debug

## Copie uploaded file to main file (because of rights)
url = HosteurRagHost + "/1.0/environment/control/rest/execcmdbyid?session=" + session + "&appid=" + appid + "&envName=" + envname + "&nodeId="+ str(nodeid) +"&commandList=[{\"command\": \"cat /var/www/jmpres/httpd.conf > /etc/httpd/conf/httpd.conf\"}]"

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text)

#  - .env (write from code or else, can't be public) to improve ...
f = open("ressources/conf/envdefault", "r")
body=f.read()

url = HosteurRagHost + "/1.0/environment/file/rest/write?session=" + session + "&appid=" + appid + "&envName=" + envname + "&nodeId="+ str(nodeid) +"&body=" + body +"&path=/var/www/webroot/ROOT/.env&isAppendMode=false"

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text) #debug

## Adding .env to favorite for easyest managment
url = HosteurRagHost + "/1.0/environment/file/rest/addfavorite?session=" + session + "&appid=" + appid + "&envName=" + envname + "&nodeId="+ str(nodeid) +"&path=/var/www/webroot/ROOT/.env&isDir=false"

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text) #debug

# Restart Apache node
url = HosteurRagHost + "/1.0/environment/control/rest/restartnodebyid?session=" + session + "&appid=" + appid + "&envName=" + envname + "&nodeId="+ str(nodeid)

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text) #debug

# Clean-up Install assets
url = HosteurRagHost + "/1.0/environment/control/rest/execcmdbyid?session=" + session + "&appid=" + appid + "&envName=" + envname + "&nodeId="+ str(nodeid) +"&commandList=[{\"command\": \"rm -rf /var/www/jmpres\"}]"

response = requests.request("GET", url, headers=headers, data=payload)
print(response.text) #debug
