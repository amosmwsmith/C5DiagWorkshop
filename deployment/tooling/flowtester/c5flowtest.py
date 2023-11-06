# Python 3.6 (minimum)
# 

import argparse
import datetime
import time
import urllib.request
import urllib.parse
import urllib.error
import ssl
import json
import time

flowStatuses = dict()

def loadFlowStatus(endpoint, authToken, vnode):
    fullEndpoint=endpoint+vnode
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(fullEndpoint)
    req.add_header('accept', 'application/json')
    req.add_header('Authorization', 'Basic '+authToken)
    req.add_header('Content-Type','application/json')
    timeDiff = 0 
    result = False
    try:
        print("Polling for flow completion statuses on vnode "+vnode)     
        resp = urllib.request.urlopen(req, context=ctx).read().decode()
    except urllib.error.HTTPError as e:
        error = e.read().decode()  # Read the body of the error response
        _json = json.loads(error)
        return False
    _json = json.loads(resp)
    for item in _json["flowStatusResponses"]:
        if item["holdingIdentityShortHash"] == vnode:
            dictResult = {}
            dictResult["vnode"] = vnode
            dictResult["success"] = False
            if item["flowError"] == None:
                if item["flowStatus"] == "COMPLETED":
                    dictResult["success"] = True
                dictResult["flowResult"] = item["flowResult"] 
            else:
                dictResult["flowResult"] = item["flowError"] 
            flowStatuses[item["clientRequestId"]] = dictResult                            


def pollComplete(endpoint, vnode, authToken, label, pollInterval, pollTimeout):

    fullEndpoint=endpoint+vnode
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(fullEndpoint)
    req.add_header('accept', 'application/json')
    req.add_header('Authorization', 'Basic '+authToken)
    req.add_header('Content-Type','application/json')
    timeDiff = 0 
    result = False
    dictResult = dict()
    timeStart = time.perf_counter()
    while result == False:
        try:
            print("Polling for flow completion status on vnode "+vnode+" with clientRequestId: "+label+"...")     
            resp = urllib.request.urlopen(req, context=ctx).read().decode()
        except urllib.error.HTTPError as e:
            error = e.read().decode()  # Read the body of the error response
            _json = json.loads(error)
            return False
        _json = json.loads(resp)
        for item in _json["flowStatusResponses"]:
            if item["clientRequestId"] == label:
                if item["flowError"] == None:
                    if item["flowStatus"] == "COMPLETED":
                        dictResult["vnode"] = item["holdingIdentityShortHash"]
                        dictResult["success"] = True
                        dictResult["flowResult"] = item["flowResult"] 
                        print("Detected flow completion status on vnode "+vnode+" with clientRequestId: "+label+"...")                 
                        return dictResult                            
                else:
                        dictResult["vnode"] = item["holdingIdentityShortHash"]
                        dictResult["success"] = False
                        dictResult["flowResult"] = item["flowError"] 
                        print("Detected flow failure status on vnode "+vnode+" with clientRequestId: "+label+". Error is "+item["flowError"])                 
                        return dictResult                            
        timeNow = time.perf_counter()
        timeDiff = timeNow-timeStart
        if timeDiff > pollTimeout:
            print("Timeout occured when polling for flow completion status on vnode "+vnode+" with clientRequestId: "+label+"...")                 
            dictResult["success"] = False
            dictResult["flowResult"] = "Timed out after: "+item["pollTimeout"] 
            return dictResult
        time.sleep(pollInterval)
    

def issueFlow(flow, endpoint, authToken, params = list(), pollInterval = 5):
    fullEndpoint=endpoint+flow["vnode"]
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(fullEndpoint)
    req.add_header('accept', 'application/json')
    req.add_header('Authorization', 'Basic '+authToken)
    req.add_header('Content-Type','application/json')
    data = dict()
    data["clientRequestId"] = flow["flowData"]["clientRequestId"]
    data["flowClassName"] = flow["flowData"]["flowClassName"]
    requestBody = dict()
    for key,value in flow["flowParams"].items():
            requestBody[key] = str(value)
    for param in params:
        fieldVal = str(flowStatuses[param["id"]][param["outputField"]])
        if "outputSubField" in param:
            subfieldDict = json.loads(fieldVal)
            fieldVal = subfieldDict["id"]
        requestBody[param["inputField"]] = fieldVal
    data["requestBody"] = requestBody
    req.data = bytes(json.dumps(data), encoding="utf-8")
    flowResponse = urllib.request.urlopen(req, context=ctx)
    print("polling for response....")
    pollResponse = pollComplete(endpoint = endpoint,vnode = flow["vnode"],authToken = authToken, label = flow["flowData"]["clientRequestId"], pollInterval = pollInterval, pollTimeout = flow["pollTimeout"])
    flowStatuses[flow["flowData"]["clientRequestId"]] = pollResponse
    return pollResponse


def runFlows(flows, endpoint, authToken, pollInterval = 5):
    for flow in flows:
        if flow["flowData"]["clientRequestId"] in flowStatuses:
            print("A flow already exists with id: "+flow["flowData"]["clientRequestId"]+" so will not be submitted." )
            continue
        if "depends" in flow:
            params = list()
            dependSuccess = True
            for depend in flow["depends"]:
                result = flowStatuses[depend["id"]]
                if result["success"] == True:                       
                   params.append(depend)                     
                else:
                    dependSuccess = False
                    print("Flow with id: "+flow["flowData"]["clientRequestId"]+"will not be run due to dependency on "+depend["id"]+" which has failed with status: "+result["flowResult"]["message"])     
                    break
            if dependSuccess == True:                        
                print("Running flow issueFlow with id:"+flow["flowData"]["clientRequestId"]+" with request id: "+ flow["flowData"]["clientRequestId"])     
                response = issueFlow(flow = flow, endpoint = endpoint, authToken = authToken, params = params, pollInterval = pollInterval)
        else:
            print("Running flow issueFlow with request id:"+ flow["flowData"]["clientRequestId"])     
            response = issueFlow(flow = flow, endpoint = endpoint, authToken = authToken)

def checkResults(flows):
    for flow in flows:
        if "expectedResults" in flow:    
            for expectedResult in flow["expectedResults"]:
                fieldName = None
                expectedVal = None
                actualVal = None
                if flow["flowData"]["clientRequestId"] in flowStatuses:
                    if "outputSubField" in expectedResult:
                        fieldName = expectedResult["outputSubField"]
                        expectedVal = expectedResult["value"]
                        jsonResult = flowStatuses[flow["flowData"]["clientRequestId"]][expectedResult["outputField"]]  
                        subfieldDict = json.loads(jsonResult)
                        actualVal = subfieldDict[fieldName]
                    else:
                        fieldName = expectedResult["outputField"]
                        expectedVal = expectedResult["value"]                
                        actualVal = flowStatuses[flow["flowData"]["clientRequestId"]][expectedResult["outputField"]] 
                    if(str(expectedVal) != str(actualVal)):
                        print("Test result failure for flow: "+flow["flowData"]["clientRequestId"]+":")    
                    else:
                        print("Test result passed for flow: "+flow["flowData"]["clientRequestId"]+":")    
                    print("Expected result is "+str(expectedVal)+" for field: "+fieldName)
                    print("Actual result is "+str(actualVal)+" for field: "+fieldName)
                else:
                    print("Actual result is missing for flow: "+flow["flowData"]["clientRequestId"])




def main():
    parser = argparse.ArgumentParser()   
    parser.add_argument('-c', '--config-file',
                            help='json file with flow configuration',
                            default='test8.json')    
    args = parser.parse_args()
    if not args.config_file:
       print("Mandatory argument not supplied for parameter --config-file")
       return
    print("Loading file: "+args.config_file)     
    try:
        f = open(args.config_file)
    except FileNotFoundError:
        print("Unable to locate file "+args.config_file)
        return
    config = json.load(f)
    for vnode in config["vnodes"]:
        loadFlowStatus(endpoint = config["endpoint"],authToken = config["authToken"], vnode = vnode)
    runFlows(config["flowSequence"], endpoint = config["endpoint"], authToken = config["authToken"], pollInterval = config["pollInterval"])
    checkResults(config["flowSequence"])

if __name__ == "__main__":
  main()
  
  