#!/bin/bash
echo Script name: $0
echo $# arguments 
if [ "$#" -ne 5 ]; then
    echo "Illegal number of parameters"
    echo "Paramaters expected: " 
    echo "1. unique flow client id label"
    echo "2. vnode hash"
    echo "3. amount"
    echo "4. issuer"
    echo "5. authtoken"
    exit
fi
label=$1
vnode=$2
amount=$3
issuer=$4
authtoken=$5
 echo "Calling issue token flow with label: $label:"
 curl -X 'POST' \
  'https://localhost:1443/api/v1/flow/'$vnode'' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic '$authtoken'' \
  -H 'Content-Type: application/json' --insecure \
  -d '{
     "clientRequestId" : "issue-cash-token-'$label'",
     "flowClassName" : "com.r3.ps.samples.concert.workflow.CashTokenIssueFlow",
	 "requestBody": {
	    "value" : '$amount',
	    "issuer": '"$issuer"'
	}
  }'
  echo "issue-cash-token-$label submitted."

