#!/bin/bash
echo Script name: $0
echo $# arguments 
if [ "$#" -ne 8 ]; then
    echo "Illegal number of parameters"
    echo "Paramaters expected: " 
    echo "1. clientRequestIdPrefix: unique flow client id prefix label"
    echo "2. shortHash: short hash value of the vnode endpoint of this request in corda-rest-worker API"
    echo "3. count: integer value representing number of iterations for the flow to be run - (current iteration number will be added to clientRequestd value for each submission)"	
    echo "4. walletId: string value containing the identifier of the wallet which will receive the token amount" 
    echo "5. tokenId: string value containing the identifier of the token used to make the deposit into the wallet"
    echo "6. amount: integer value representing the amount of cash to be deposited in the wallet"
    echo "7. authToken: the auth token used to submit the request"
    echo "8. sleepInterval: interval in seconds to wait between each submission"	
    exit
fi
label=$1
vnode=$2
count=$3
walletid=$4
tokenid=$5
amount=$6
authtoken=$7
sleepInterval=$8
for (( c=1; c<=$count; c++ ))
do
 echo "Iteration $c of $count. Calling deposit cash token flow - depositing cash token id: $tokenid into wallet id: $walletid with amount: $amount"
 curl -X 'POST' \
  'https://localhost:1443/api/v1/flow/'$vnode'' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic '$authtoken'' \
  -H 'Content-Type: application/json' --insecure \
  -d '{
     "clientRequestId" : "deposit-cash-token-'$label-$c'",
     "flowClassName" : "com.r3.ps.samples.concert.workflow.DepositCashToken",
	 "requestBody": {
			"tokenId" : "'$tokenid'",
			"walletId" : "'$walletid'",
			"amount" : '$amount'
	}
  }'
  echo "deposit-cash-token-$label-$c submitted."
sleep $sleepInterval
done
