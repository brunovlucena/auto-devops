# This Service:
# - Receives a CloudEvent network.notifi.lambda.build.start
# - Creates a Kaniko Job to build the image
# - Use Golang

# It should create a context for kaniko.
# 1) Downloads s3://[ThirdPartyId]/[ParserId].js"
# 2) It packs together wrapper.js Dockerfile and [ParserId].js. 
# 3) It should uploads [ParserId].tar.gz to  s3://[ThirdPartyId]/[ParserId].tar.gz" 