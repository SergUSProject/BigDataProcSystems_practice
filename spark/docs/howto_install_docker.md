# Установка Docker и Docker-Compose

Усовик С.В. (usovik@bmstu.ru)



## Содержание

- [Установка Docker](#Установка-Docker)
- [Установка Docker Compose](#Установка-Docker-Compose)
- [Замечания](#Замечания)


## Установка Docker

```
sudo apt update

sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"


sudo apt-get install -y \
    docker-ce=5:19.03.14~3-0~ubuntu-bionic \
    docker-ce-cli=5:19.03.14~3-0~ubuntu-bionic \
    containerd.io=1.3.9-1
```

Отобразить версию docker:
```cmd
ubuntu@linux:~$ docker --version
Docker version 19.03.14, build 5eb3275d40
```

`sudo docker run hello-world`

```cmd
ubuntu@linux:~$ sudo docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
0e03bdcc26d7: Pull complete 
Digest: sha256:1a523af650137b8accdaed439c17d684df61ee4d74feac151b5b337bd29e7eec
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

Но когда вы запускаете ту же команду без привилегий root, вы получаете следующую ошибку:

```
docker: Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Post http://%2Fvar%2Frun%2Fdocker.sock/v1.40/containers/create: dial unix /var/run/docker.sock: connect: permission denied.
```

TЧтобы избавиться от префикса `sudo` при запуске команд `docker`, выполните следующие действия.

Создайте группу `docker`, если она не существует:

`sudo groupadd docker`

Добавьте текущего пользователя в группу `docker`:

 `sudo usermod -G docker -a $USER`

Примените изменения (только для Linux, в противном случае перезагрузите систему):

`newgrp docker`

Проверьте, все ли работает правильно:

`docker run hello-world`


## Установка Docker Compose

`sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose`

Если возникает ошибка "ERROR: client and server don't have same version (client : 1.38, server: 1.18)", то загрузите другую совместимую версию docker-compose [отсюда](../docker/compose/releases)

Сделать его исполняемым:

`sudo chmod +x /usr/local/bin/docker-compose`

Создайте ссылку на `docker-compose`, чтобы использовать ее в каталоге `/usr/bin`:

`sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose`

Теперь проверьте, работает ли `docker-compose`, распечатав его версию:

```cmd
ubuntu@linux:~$ docker-compose --version
docker-compose version 1.27.4, build 40524192
```


## Замечания

- [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/) (official doc)
- [Post-installation steps for Linux](https://docs.docker.com/engine/install/linux-postinstall/) (official doc)
- [Install Docker Compose](https://docs.docker.com/compose/install/) (official doc)