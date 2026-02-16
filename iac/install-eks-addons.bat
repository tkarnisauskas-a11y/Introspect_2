@echo off
REM Install EKS Addons for introspect-2-cluster

set CLUSTER_NAME=introspect-2-cluster
set REGION=us-east-1

echo Installing EKS addons for cluster: %CLUSTER_NAME%

echo Installing vpc-cni addon...
aws eks create-addon --cluster-name %CLUSTER_NAME% --addon-name vpc-cni --region %REGION%

echo Installing coredns addon...
aws eks create-addon --cluster-name %CLUSTER_NAME% --addon-name coredns --region %REGION%

echo Installing kube-proxy addon...
aws eks create-addon --cluster-name %CLUSTER_NAME% --addon-name kube-proxy --region %REGION%

echo Installing aws-ebs-csi-driver addon...
aws eks create-addon --cluster-name %CLUSTER_NAME% --addon-name aws-ebs-csi-driver --region %REGION%

echo Installing amazon-cloudwatch-observability addon...
aws eks create-addon --cluster-name %CLUSTER_NAME% --addon-name amazon-cloudwatch-observability --region %REGION%

echo Done! Check addon status with:
echo aws eks describe-addon --cluster-name %CLUSTER_NAME% --addon-name [addon-name] --region %REGION%
