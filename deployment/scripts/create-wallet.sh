#!/bin/bash
echo Script name: $0
echo $# arguments 
if [ "$#" -ne 4 ]; then
    echo "Illegal number of parameters"
    echo "Paramaters expected: " 
    echo "1. unique flow client id label"
    echo "2. vnode hash"
    echo "3. payee name"
    echo "4. authtoken"
    exit
fi

 label=$1
 vnode=$2
 payee=$3
 authtoken=$4
 echo "Calling create wallet flow with label $label"
 curl -X 'POST' \
  'https://localhost:1443/api/v1/flow/'$vnode'' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic '$authtoken'' \
  -H 'Content-Type: application/json' --insecure \
  -d '{
     "clientRequestId" : "create-wallet-'$label'",
     "flowClassName" : "com.r3.ps.samples.concert.workflow.CreateWalletFlow",
     "requestBody": {
	  "ownerName" : "'$payee'"
     }
  }'
  echo "create-wallet-$label submitted."
