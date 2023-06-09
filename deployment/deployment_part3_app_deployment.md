# C5DiagWorkshop Deployment Steps - CORDAPP DEPLOYMENT

## Step 1 - download the CorDapp from the repository to your local machine in a new folder named "c5_beta3_hc03"

```
wget https://github.com/amosmwsmith/C5DiagWorkshop/blob/main/deployment/cordapp/c5-cordapp-sample-kotlin.zip
```

## Step 2 - cd into that folder and extract the contents of the zip into that folder

## Step 3 - create a new folder called "beta3" and cd into that folder

## Step 4 - open a terminal and run the below commands to pull the required images for the build:

### 1. Download Helm charts (on your local machine)
```
   wget https://staging.download.corda.net/c5-release-pack/5582b6dd-5cd4-45a1-8b16-cd9f7fa09737-Hawk1.0-RC03/corda-5.0.0-beta.3-RC.3.tgz 
```

### 2. Download Dev Pack
```
wget https://staging.download.corda.net/c5-release-pack/5582b6dd-5cd4-45a1-8b16-cd9f7fa09737-Hawk1.0-RC03/cordApp-dev-pack-Hawk1.0-RC03.tar.gz
```

### 3. Download Worker Images
```
wget https://staging.download.corda.net/c5-release-pack/5582b6dd-5cd4-45a1-8b16-cd9f7fa09737-Hawk1.0-RC03/corda-worker-images-Hawk1.0-RC03.tar
```

### 4. Download Platform Jars
```
wget https://staging.download.corda.net/c5-release-pack/5582b6dd-5cd4-45a1-8b16-cd9f7fa09737-Hawk1.0-RC03/platform-jars-Hawk1.0-RC03.tar.gz
```

### 5. Extract platform jars

```
tar -xzvf  platform-jars-Hawk1.0-RC03.tar.gz
```

### 6. Extract Dev Pack

```
tar -xzvf  cordApp-dev-pack-Hawk1.0-RC03.tar.gz
```

## Step 5 - create environment variable to store the path to the beta3 folder

```
export C5_DEPS = your_local_path/c5_beta3_hc03/beta3
```

## Step 6 - get the initial_admin_user password (run this on the VM with the deployed cluster)

```
 kubectl get secret -n corda corda-initial-admin-user -o jsonpath='{.data.password}'| base64 --decode; echo;
 ```

## Step 7 - assign the password extracted from step 7 into the gradle.properties file under c5-cordapp-sample-kotlin folder

```
cordaRpcPasswd=[password]
```

## Step 8 - run the following command to connect to the remote VM and direct the 1443 port output on the VM to same 1443 port on your local machine

```
ssh -i [PEM file] -gL 1443:localhost:1443 azureuser@[VM IP]
```

## Step 9 - run command on the remote VM to forward traffic on port 1443 to the rest worker service on port 443 

```
kubectl port-forward svc/corda-rest-worker 1443:443
```
## Step 10 - run CLI command (run this on your local machine)

```
cd /home/azureuser/c5_beta3_hc03/beta3/net/corda/cli/deployment/corda-cli-installer/5.0.0.0-Hawk1.0-RC03/corda-cli-installer-5.0.0.0-Hawk1.0-RC03
unzip corda-cli-installer-5.0.0.0-Hawk1.0-RC03.zip
chmod 755 install.sh
./install.sh
```

## Step 11 - run steps to deploy the Cordapp (on your local development machine)

N.B before running below steps make sure you have Java 11 installed (Now you must have Java 11 installed; install specifically 11.0.17) and JAVA_HOME variable is correctly set to that version.

```
cd [your_local_path]/c5-cordapp-sample-kotlin
chmod 755 gradlew
./gradlew clean build
cd [your_local_path]/c5-cordapp-sample-kotlin/concert-scenario-workflows 
../gradlew :concert-scenario-workflows:1-createGroupPolicy
../gradlew :concert-scenario-workflows:2-createKeyStore
../gradlew :concert-scenario-workflows:3-buildCPIs
../gradlew :concert-scenario-workflows:4-deployCPIs
../gradlew :concert-scenario-workflows:5-createAndRegVNodes
```

