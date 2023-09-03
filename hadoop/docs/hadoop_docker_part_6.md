# Hadoop на Docker. Чаcть 6: Составление Compose для Swarm

Усовик С.В. (usovik@bmstu.ru)

## Содержание

- Запуск Swarm с частным реестром
- Docker-compose для Swarm
- Развертывание Hadoop при помощи docker-compose
- Запуск MapReduce-приложения
- Очистка
- Рекомендации

## Предыдущие шаги

- [Part 1: Введение](hadoop_docker_part_1.md)
- [Part 2: Создание базового образа Hadoop](hadoop_docker_part_2.md)
- [Part 3: Создание образов Hadoop Master и Worker](hadoop_docker_part_3.md)
- [Part 4: Развертывание при помощи Docker Compose и запуск MapReduce-приложения](hadoop_docker_part_4.md)
- [Part 5: Развертывание на нескольких хостах в режиме Docker Swarm](hadoop_docker_part_5.md)

## Запуск Swarm при помощи частного реестра

Как активировать режим Swarm и запустить приватный реестр смотрите [здесь](hadoop_docker_part_5.md).

## Docker-compose для Swarm

В docker-compose нет флага `replicas-max-per-node`. Таким образом, рабочий сервис будет развернут с использованием `global` режима (одна реплика на узел).

```yml
version: "3.7"

services:
  master:     # Master Service
    image: 192.168.5.5:5000/hadoop-master-image
    ports:
      - target: 9870      # Namenode
        published: 9870
        protocol: tcp
        mode: host
      - target: 8088      # Resource Manager
        published: 8088
        protocol: tcp
        mode: host
      - target: 19888     # History Server
        published: 19888
        protocol: tcp
        mode: host
    deploy:
      mode: replicated
      replicas: 1
      endpoint_mode: dnsrr
      placement:
        constraints:
          - node.role == manager
    volumes: 
      - ./app:/app     # jar files
      - ./data:/data   # data to copy to HDFS
    networks:
      - hadoop-network

  worker:     # Worker Service
    image: 192.168.5.5:5000/hadoop-worker-image
    networks:
      - hadoop-network
    deploy:
      mode: global
      resources:
        limits:
            cpus: "1"
            memory: 1G

networks:
  hadoop-network: # Network
    driver: overlay
    ipam:
      config:
      - subnet:  10.0.1.0/24
```

## Развертывание Hadoop при помощи docker-compose

Перед запуском кластера все связанные образы должны быть помещены в реестр.

### Запуск кластера

Используйте команду `docker stack deploy`, чтобы развернуть кластер с помощью файла compose:

`docker stack deploy --compose-file swarm.docker-compose.yml hadoop`

Проверяем, все ли сервисы работают нормально:

`docker stack services hadoop`

```
ID                  NAME                MODE                REPLICAS            IMAGE                                         PORTS
89oec9tzb1kx        hadoop_master       replicated          1/1                 192.168.5.5:5000/hadoop-master-image:latest   
igc8j47zd5nq        hadoop_worker       global              2/2                 192.168.5.5:5000/hadoop-worker-image:latest
```

Показать все задачи, связанные с сервисом worker:

`docker service ps hadoop_worker`

```
ID                  NAME                                      IMAGE                                         NODE                DESIRED STATE       CURRENT STATE                ERROR               PORTS
tq4c36o1sne7        hadoop_worker.og36lgyz7xi58yivz17sy92gk   192.168.5.5:5000/hadoop-worker-image:latest   vhost-2             Running             Running 23 seconds ago                           
vofpyddl1ncs        hadoop_worker.dfsyvavxzazo83acguqzhbhuk   192.168.5.5:5000/hadoop-worker-image:latest   vhost-1             Running             Running about a minute ago 
```

Показать все задачи, связанные с сервисом manager:

`docker ps`

```
CONTAINER ID        IMAGE                                         COMMAND                  CREATED             STATUS              PORTS                                                                      NAMES
6a27a56412b1        192.168.5.5:5000/hadoop-master-image:latest   "sh /usr/local/bin/e…"   4 minutes ago       Up 4 minutes        0.0.0.0:8088->8088/tcp, 0.0.0.0:9870->9870/tcp, 0.0.0.0:19888->19888/tcp   hadoop_master.1.nk83wv5ad7kctqkd5ucushxi5
a212c1fca052        192.168.5.5:5000/hadoop-worker-image:latest   "sh /usr/local/bin/e…"   4 minutes ago       Up 4 minutes                                                                                   hadoop_worker.dfsyvavxzazo83acguqzhbhuk.vofpyddl1ncsgreprssu8lcaw
4c4dac25960a        registry:2                                    "/entrypoint.sh /etc…"   22 minutes ago      Up 22 minutes       5000/tcp                                                                   registry.1.mlqg8m7plg5nvbbavzqascanq
```

Показать все контейнеры на узле worker:

`docker ps`

```
CONTAINER ID        IMAGE                                         COMMAND                  CREATED             STATUS              PORTS               NAMES
e8e31d81c4a2        192.168.5.5:5000/hadoop-worker-image:latest   "sh /usr/local/bin/e…"   4 minutes ago       Up 4 minutes                            hadoop_worker.og36lgyz7xi58yivz17sy92gk.tq4c36o1sne7x2191le1qvhea
```

### Инспектирование Hadoop демонов

#### Служба logs

`docker service logs hadoop_master`

```
hadoop_master.1.nk83wv5ad7kc@vhost-1    | Start SSH service
hadoop_master.1.nk83wv5ad7kc@vhost-1    | Starting OpenBSD Secure Shell server: sshd.
hadoop_master.1.nk83wv5ad7kc@vhost-1    | Start Hadoop daemons
hadoop_master.1.nk83wv5ad7kc@vhost-1    | The entrypoint script is completed
```

`docker service logs hadoop_worker`

```
hadoop_worker.0.tq4c36o1sne7@vhost-2    | Start SSH service
hadoop_worker.0.tq4c36o1sne7@vhost-2    | Starting OpenBSD Secure Shell server: sshd.
hadoop_worker.0.tq4c36o1sne7@vhost-2    | Start Hadoop daemons
hadoop_worker.0.tq4c36o1sne7@vhost-2    | WARNING: /home/bigdata/hadoop/logs does not exist. Creating.
hadoop_worker.0.vofpyddl1ncs@vhost-1    | Start SSH service
hadoop_worker.0.vofpyddl1ncs@vhost-1    | Starting OpenBSD Secure Shell server: sshd.
hadoop_worker.0.vofpyddl1ncs@vhost-1    | Start Hadoop daemons
hadoop_worker.0.vofpyddl1ncs@vhost-1    | WARNING: /home/bigdata/hadoop/logs does not exist. Creating.
```

#### HDFS

`docker exec $(docker ps --filter name=master --format "{{.ID}}") bash hdfs dfsadmin -printTopology`

```
Rack: /default-rack
   10.0.1.3:9866 (hadoop_worker.dfsyvavxzazo83acguqzhbhuk.vofpyddl1ncsgreprssu8lcaw.hadoop_hadoop-network)
   10.0.1.4:9866 (hadoop_worker.og36lgyz7xi58yivz17sy92gk.tq4c36o1sne7x2191le1qvhea.hadoop_hadoop-network)
```

#### YARN

`docker exec $(docker ps --filter name=master --format "{{.ID}}") bash yarn node --list`

```
INFO client.RMProxy: Connecting to ResourceManager at master/10.0.1.7:8032
Total Nodes:2
         Node-Id             Node-State Node-Http-Address       Number-of-Running-Containers
a212c1fca052:45454              RUNNING a212c1fca052:8042                                  0
e8e31d81c4a2:45454              RUNNING e8e31d81c4a2:8042                                  0
```


## Запуск MapReduce-приложения

Скопируйте локальные данные в HDFS:

`docker exec $(docker ps --filter name=master --format "{{.ID}}") bash hdfs dfs -copyFromLocal /data /`

Проверяем, были ли скопированы данные:

`docker exec $(docker ps --filter name=master --format "{{.ID}}") bash hdfs dfs -ls /data`

```
Found 2 items
-rw-r--r--   3 bigdata supergroup 1478965298 2020-01-02 17:10 /data/reviews.json
-rw-r--r--   3 bigdata supergroup      69053 2020-01-02 17:10 /data/samples_100.json
```

Запуск MapReduce-приложения:

```
docker exec $(docker ps --filter name=master --format "{{.ID}}") bash \
    yarn jar /app/average-rating-app-1.1.jar \
        -D mapreduce.job.reduces=2 \
        /data/reviews.json \
        /data/output/ratings/
```

```
...
INFO impl.YarnClientImpl: Submitted application application_1577985546913_0001
INFO mapreduce.Job: The url to track the job: http://master:8088/proxy/application_1577985546913_0001/
INFO mapreduce.Job: Running job: job_1577985546913_0001
INFO mapreduce.Job: Job job_1577985546913_0001 running in uber mode : false
INFO mapreduce.Job:  map 0% reduce 0%
INFO mapreduce.Job:  map 9% reduce 0%
INFO mapreduce.Job:  map 28% reduce 0%
INFO mapreduce.Job:  map 39% reduce 0%
INFO mapreduce.Job:  map 70% reduce 0%
INFO mapreduce.Job:  map 89% reduce 0%
INFO mapreduce.Job:  map 93% reduce 12%
INFO mapreduce.Job:  map 100% reduce 12%
INFO mapreduce.Job:  map 100% reduce 18%
INFO mapreduce.Job:  map 100% reduce 100%
INFO mapreduce.Job: Job job_1577985546913_0001 completed successfully
...
```

Проверьте вывод:

`docker exec $(docker ps --filter name=master --format "{{.ID}}") bash hdfs dfs -head /data/output/ratings/part-r-00000`

```
0528881469      2.4
0594451647      4.2
0594481813      4.0
0972683275      4.461187214611872
1400501466      3.953488372093023
1400501776      4.15
1400532620      3.6097560975609757
...
```


## Очистка

`docker stack rm hadoop`

```
Removing service hadoop_master
Removing service hadoop_worker
Removing network hadoop_hadoop-network
```

`docker service rm registry`

```
registry
```

`docker swarm leave`

```
Node left the swarm.
```

`docker swarm leave --force`

```
Node left the swarm.
```

## Рекомендации

- [Deploy a stack to a swarm](https://docs.docker.com/engine/swarm/stack-deploy/)
- [Docker stack commands](https://docs.docker.com/engine/reference/commandline/stack/)
- [Compose file version 3 reference](https://docs.docker.com/compose/compose-file/)
- [Deploy Docker Compose (v3) to Swarm (mode) Cluster](https://codefresh.io/docker-tutorial/deploy-docker-compose-v3-swarm-mode-cluster/)

