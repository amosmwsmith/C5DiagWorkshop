#!/bin/bash
if [ -z "$1" ]; then
 echo "Specify target registry"
 exit 1
fi

declare -a images=(
 "corda-os-rest-worker" "corda-os-flow-worker"
 "corda-os-member-worker" "corda-os-p2p-gateway-worker"
 "corda-os-p2p-link-manager-worker" "corda-os-db-worker"
 "corda-os-crypto-worker" "corda-os-plugins" )
tag=5.0.0.0-Beta3-HC03
target_registry=$1

for image in "${images[@]}"; do
 source=corda/$image:$tag
 target=$target_registry/$image:$tag
 echo "Publishing image $source to $target"
 docker tag $source $target
 docker push $target
done

docker tag postgres:14.4 $target_registry/postgres:14.4
docker push $target_registry/postgres:14.4
