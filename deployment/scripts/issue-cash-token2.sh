#!/bin/bash
echo Script name: $0
echo $# arguments 
if [ "$#" -ne 7 ]; then
    echo "Illegal number of parameters"
    echo "Paramaters expected: " 
    echo "1. unique flow client id label"
    echo "2. vnode hash"
    echo "3. amount"
    echo "4. issuer"
    echo "5. authtoken"
    echo "6. count"
    echo "7. sleepInterval"
    exit
fi
label=$1
vnode=$2
amount=$3
issuer=$4
authtoken=$5
count=$6
sleepInterval=$7
for (( c=1; c<=$count; c++ ))
do
 echo "Calling issue token flow with label: $label-$c:"
 curl -X 'POST' \
  'https://localhost:1443/api/v1/flow/'$vnode'' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic '$authtoken'' \
  -H 'Content-Type: application/json' --insecure \
  -d '{
     "clientRequestId" : "issue-cash-token-'$label-$c'",
     "flowClassName" : "com.r3.ps.samples.concert.workflow.CashTokenIssueFlow",
	 "requestBody": {
	    "value" : '$amount',
	    "issuer": '"$issuer"'
	}
  }'
  echo "issue-cash-token-$label-$c submitted."
  sleep $sleepInterval
done
