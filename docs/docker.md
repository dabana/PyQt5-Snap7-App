```
# remove all images
sudo docker rmi $(sudo docker images -a -q)

# remove all images (powershell)
docker images -q | %{docker rmi -f $_}

# remove all exited containers
sudo docker rm $(sudo docker ps -a -f status=exited -q)

# remove all exited containers (powershell)
docker ps -a -q | % { docker rm $_ }

# force stop and remove all containers
docker rm -f $(docker ps -a -q)

# create image from container
docker commit NAME flight212121/repo:tag

# reattach to container
docker attach CONTAINER_NAME

```
