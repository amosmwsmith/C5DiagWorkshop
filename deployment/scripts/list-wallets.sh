#!/bin/bash
echo Script name: $0
if [ "$#" -ne 3 ]; then 
    echo "Illegal number of parameters"
    echo "Parameters expected: " 
    echo "1. unique flow client id label"
    echo "2. shortHash: short hash value of the vnode endpoint of this request in corda-rest-worker API"
    echo "3. authToken: the auth token used to submit the request"
    exit
fi

 echo "Calling list wallet flow:"
 
 label=$1
 vnode=$2
 authToken=$3
 curl -X 'POST' \
  'https://localhost:1443/api/v1/flow/'$vnode'' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic '$authToken'' \
  -H 'Content-Type: application/json' --insecure \
  -d '{
     "clientRequestId" : "list-wallet-'$label'",
     "flowClassName" : "com.r3.ps.samples.concert.workflow.ListWallets",
	 "requestBody": {
	}
  }'
  echo "list-wallet-flow-$label submitted."

