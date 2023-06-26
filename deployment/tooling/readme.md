# C5FlowTester - Flow Testing Tool 

## Description

 
This is a python program that can be used to test sequences of Corda 5 flows.   

Since there are already test frameworks such as Craft that can be used for Unit testing in development, this tool is primarily intended to be used in integration testing stage to test the end to end interaction between flows. It can be used test and end to end sequence of flows, taking input(s) of one or more flows to another flow, and specifying expected results.

## How the program works

The program will load the JSON config containing the specified flow sequence definition, and for each flow in the sequence check for any existing flow results via the corda rest worker flow endpoint (on the specified cluster) in case any results already exist based on the specified Identifiers for each configured flow.

If the flow result already exists the program will not try to submit the flow, it will instead load the result into the results cache which can then be referenced as input to other dependent flows, or checked against an expected result.  

Otherwise if the result does not exist, the program will submit each configured flow via the corda rest worker endpoint and then poll for the results. Once the results are available the results are loaded into the results cache.  

## Running the program

Simply run the below command

```
python c5flowtest.py -c template.json
```

..where the template.json is your customised json file name used to specify configuration and inputs and outpus

A single JSON file is used as input to specify the target environment, configuration as well as all inputs and outputs.

## Description of the JSON file format

### There are 4 global settings as required inputs as follows:

```
1. endpoint: this is the endpoint for the corda-rest-worker on the Corda 5 cluster which will be used to submit flows to the flow workers in that cluster.

2. authToken: this is the initial admin user password for your deployed cluster.

3. vnodes: this is an array containing the short hash code of each virtual node used to run flows. This is necessary to fetch any existing results to load into the cache at the start of the program.

4. pollInterval: this is an integer value used to specify the interval in seconds to wait before checking the results. The results for each configured fllow will be checked according to this interval up until the pollTimeout value for each flow. This pollTimeout value is defined for each individual flow.
```

### The flowSequence section of the JSON file definines a list of flows and any dependencies between them.

These are the possible parameters for each flow entry:

```
1. vnode: this is the short code hash of the virtual node which is the target of the flow submission.

2. pollTimeout: this is the number of seconds for which the program will keep polling for results every x seconds, where x is the time interval (specified in seconds) specified in pollInterval. After this time an timeout error is recorded in the flowResult.

3. flowData: this is an array containing 2 variables:

	flowClassName: the full class path to the flow to be checked / submitted
	clientRequestId: the unique identifier for the submitted flow

4. flowParams: this is an array of key value pairs. Each entry int he array is a paremeter name with the value for that flow parameter:

5. depends: this an optional setting. If specified it must contain an array of 3 key value pairs, each entry in the array represents a dependency of a specific input to the flow from a previous flow's result.
For each entry in the array:
- The first entry in the  with key "id" represents the unique identifier for a dependent flow for which results are required as input to this flow. 
- The second entry with key "outputField" is the name of the dependnet field in the result set returned from this flow. This value will be cached and used as input for the 3rd entry.
- The third entry with key "inputField" specifies the exact parameter name to receive the input value from the second entry. The value is taken from from the second entry.

6. expectedResults: this an optional setting. If specified it must contain an array of up to 3 key value pairs (minimum 2), with each entry in the array representing an expected result of the return value of the flow. These expected results are then compared with the actual results and are reported at runtime.
For each entry in the array:
- The 1st entry with key "value" specifies a discrete value as the expected result. The data type is inferred from the corresponding value supplied for the entry.
- The 2nd entry with key "outputField" is the name of the field which contains the result of the flow obtained via a call to the "GET" endpoint of the Flow Management API accessed via the "corda-rest-worker" component. Typically this is "flowResult" but is specified explicitly in case of future changes. If there is only one discerete output value in the flowResult, then do not specify a 3rd entry - the expected result value in 1st entry is then compared directly with the value obtained in the flow result. 
- The 3rd entry "outputSubField" is optional to be specified in the case where the flow result contains an array of parameter key / values. The expected result in 1st entry with key "value" is compared with the actual result returned in this field. 
```

## Example Configuration

Example JSON file is provided below based on a minikube cluster running Corda 5.

Here there are 3 flows: 

"CashTokenIssueFlow" and "CreateWalletFlow" the results of which then provide input values to "DepositCashToken" flow.

The expected result of the "DepositCashToken" flow is then compared with the actual result.

```
{
	"endpoint": "https://localhost:1443/api/v1/flow/",
	"authToken": "YWRtaW46QmlWM2N3V2xnWWRo",
	"vnodes": ["FF589770AA64"],
	"pollInterval": 5,		
	"flowSequence": [{
			"vnode": "FF589770AA64",
			"pollTimeout": 120,
			"flowData": {
				"flowClassName": "com.r3.ps.samples.concert.workflow.CashTokenIssueFlow",
				"clientRequestId": "issue-cash-token-b4-1"
			},
			"flowParams": {
				"value": 10,
				"issuer": "CN=PSP1,OU=Test Dept, O=R3, L=London, C=GB"
			}
		},
		{
			"vnode": "FF589770AA64",
			"pollTimeout": 120,
			"flowData": {
				"flowClassName": "com.r3.ps.samples.concert.workflow.CreateWalletFlow",
				"clientRequestId": "create-wallet-b4-1"
			},
			"flowParams": {
				"ownerName": "Payee-1"
			}
		},
		{
			"vnode": "FF589770AA64",
			"pollTimeout": 120,
			"depends": [{
				"id": "issue-cash-token-b4-1",
				"outputField": "flowResult",
				"inputField": "tokenId"				
			},
			{
				"id": "create-wallet-b4-1",
				"outputField": "flowResult",
				"outputSubField": "id",
				"inputField": "walletId"				
			}			
			],
			"flowData": {
				"flowClassName": "com.r3.ps.samples.concert.workflow.DepositCashToken",
				"clientRequestId": "deposit-wallet-b4-1"
			},
			"flowParams": {
				"amount": "2"
			},
			"expectedResults": [
			 { 
				"value": 3.0,
				"outputField": "flowResult",
				"outputSubField": "cashBalance" 
			 }
			]
		}				
	]

}
```
