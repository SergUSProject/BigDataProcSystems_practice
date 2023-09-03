# Установка Minikube

Усовик С.В. (usovik@bmstu.ru)


## Установка kubectl на Linux:

Загрузка инструментов командной строки `Kubernetes`:

`wget -P $HOME/Downloads https://storage.googleapis.com/kubernetes-release/release/v1.17.0/bin/linux/amd64/kubectl`

Затем создайте каталог `/usr/local/bin`, если необходимо, переместите инструмент в каталог и измените разрешение, чтобы сделать исполняемый файл доступным для всех пользователей:

```bash
sudo mkdir -p /usr/local/bin \
  && sudo mv $HOME/Downloads/kubectl $_ \
  && sudo chmod +x /usr/local/bin/kubectl
```

Если каталога нет в вашей переменной `PATH`, добавьте его с помощью следующей команды (лучший способ — добавить эту строку в файл `.profile` вашего текущего пользователя):

`export PATH=/usr/local/bin:$PATH`

Теперь проверьте, все ли в порядке, напечатав версию `kubectl`:

`kubectl version`

```
Client Version: version.Info{Major:"1", Minor:"17", GitVersion:"v1.17.0", GitCommit:"70132b0f130acc0bed193d9ba59dd186f0e634cf", GitTreeState:"clean", BuildDate:"2019-12-07T21:20:10Z", GoVersion:"go1.13.4", Compiler:"gc", Platform:"linux/amd64"}
The connection to the server localhost:8080 was refused - did you specify the right host or port?
```


## Установите minikube

Загрузите `minikube`, инструмент для разработки локальных приложений Kubernetes:

`wget -O $HOME/Downloads/minikube /opt/k8s/minikube https://storage.googleapis.com/minikube/releases/v1.6.1/minikube-linux-amd64`

Так же, как и для `kubectl`, при необходимости создайте каталог `/usr/local/bin`, переместите инструмент в каталог и измените разрешение, чтобы сделать файл исполняемым для всех пользователей:

```bash
sudo mkdir -p /usr/local/bin \
  && sudo mv $HOME/Downloads/minikube $_ \
  && sudo chmod +x /usr/local/bin/minikube
```

Теперь проверьте свою версию `minikube`:

`minikube version`

```
minikube version: v1.6.1
```

## Рекомендации

[Install and Set Up kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl-on-linux)

[Install Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/)