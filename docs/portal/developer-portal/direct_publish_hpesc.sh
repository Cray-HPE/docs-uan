<<<<<<< HEAD
curl -v -X POST -H "X-Communication-Id: $X_COMMUNICATION_ID" -H "X-Auth-Token: $X_AUTH_TOKEN" -H "Content-Type: multipart/form-data" -F "file=@build/install/crs8032_1en_us.zip" 'https://api.support.hpe.com/document-loader/v1/pushcontent/';
curl -v -X POST -H "X-Communication-Id: $X_COMMUNICATION_ID" -H "X-Auth-Token: $X_AUTH_TOKEN" -H "Content-Type: multipart/form-data" -F "file=@build/admin/crs8033_1en_us.zip" 'https://api.support.hpe.com/document-loader/v1/pushcontent/'
=======
curl -v -X POST -H "X-Communication-Id: $X_COMMUNICATION_ID" -H "X-Auth-Token: $X_AUTH_TOKEN" -H "Content-Type: multipart/form-data" -F "file=@build/install/crs8032_3en_us.zip" 'https://api.support.hpe.com/document-loader/v1/pushcontent/';
curl -v -X POST -H "X-Communication-Id: $X_COMMUNICATION_ID" -H "X-Auth-Token: $X_AUTH_TOKEN" -H "Content-Type: multipart/form-data" -F "file=@build/admin/crs8033_3en_us.zip" 'https://api.support.hpe.com/document-loader/v1/pushcontent/'
>>>>>>> e1e508fe06dc57f525154576b059fa72b01b7d28
