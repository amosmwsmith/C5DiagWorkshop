# C5DiagWorkshop Deployment Steps - CORDA DEPLOYMENT

## Step 1: (Optional) Create container registry in Azure to store images. N.B This should be done on your client machine not the VM by following the steps below:

### 1. Download the worker images:	

```
wget https://staging.download.corda.net/c5-release-pack/e7a4dbd4-2694-4ba9-b931-8f9340267b4f-Beta3-HC01/corda-worker-images-Beta3-HC01.tar
```

### 2. Load the docker images into your local docker instance:

```
docker load -i corda-worker-images-Beta3-HC01.tar
```

### 3. Log into your container registry:

```
docker login [registry name]
```

### 4. Download push script in the git hub repository here:

```
git clone git@github.com:amosmwsmith/C5DiagWorkshop.git
```

### 5. Run the script to push the images

```
./push.sh
```

## Step 2: Download the helm charts for Beta3 HC01 (Run on the Azure VM):

```
wget https://staging.download.corda.net/c5-release-pack/e7a4dbd4-2694-4ba9-b931-8f9340267b4f-Beta3-HC01/corda-0.4.0.tgz
```

## Step 3 - Create namespace corda and set as default (Run on Azure VM)

```
kubectl create namespace corda
kubectl config set-context --current --namespace=corda
```

## Step 4 - Run command to create secret necessary to access Corda images in repository (Run on Azure VM - replace values with your own container registry if needed)

```
kubectl create secret -n corda docker-registry cred04 --docker-server c5diagnosticsregistry.azurecr.io --docker-username C5DiagnosticsRegistry --docker-password "Mac83jbBp0EnIU+OnfOPbK5hVHXdSV02Rjx7quoIDT+ACRCI1K4y"
```

## Step 5 - Install Kafka (Run on Azure VM)

```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install kafka bitnami/kafka --version 19.1.0 --values ~/C5DiagWorkshop/deployment/yaml_files/kafka.yaml --wait
```

## Step 6 - Install Postgres (run on Azure VM)

```
helm install postgres bitnami/postgresql --wait  --values ~/C5DiagWorkshop/deployment/yaml_files/postgres.yaml --wait
```

## Step 7 - Install Corda (run on Azure VM)

```
helm upgrade --install corda corda-0.4.0.tgz --values ~/C5DiagWorkshop/deployment/yaml_files/corda.yaml --wait
```

## Step 8 - Run kubectl command (on Azure VM) to verify status is ok

```
kubectl get pods
```

Expected result - you should see a set of pods similar to below

```
NAME                                             READY   STATUS      RESTARTS       AGE
corda-create-topics-6xblk                        0/1     Completed   0              2d4h
corda-crypto-worker-74ccdf9675-f5qks             1/1     Running     0              2d4h
corda-db-worker-7674f6bc69-f5jzv                 1/1     Running     0              2d4h
corda-flow-worker-797bcb9d9-2spgv                1/1     Running     0              47h
corda-membership-worker-8554b4866f-jf9gf         1/1     Running     0              2d4h
corda-p2p-gateway-worker-666fc6cd9d-pvgn4        1/1     Running     0              2d4h
corda-p2p-link-manager-worker-568844f7cb-5cn89   1/1     Running     0              2d4h
corda-rest-worker-b98f8c78f-dwwzh                1/1     Running     0              2d4h
corda-setup-db-xtvrd                             0/1     Completed   0              2d4h
corda-setup-rbac-hfzhm                           0/3     Completed   0              2d4h
kafka-0                                          1/1     Running     1 (2d4h ago)   2d4h
kafka-zookeeper-0                                1/1     Running     0              2d4h
postgres-postgresql-0                            1/1     Running     0              2d4h
```


