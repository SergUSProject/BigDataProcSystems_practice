# Apache Spark



## Основы Spark



#### Практика:
- [Конфигурация Spark на YARN](docs/spark_basics.md)
- [Введение в PySpark RDD API](/notebooks/spark_rdd_basics.ipynb)
- [Introduction to PySpark DataFrame API](/notebooks/spark_df_basics.ipynb)
- Spark и обработка пользовательских отзывов:
    - Часть 1. Интерактивная оболочка при помощи Jupyter ([Python](/notebooks/spark_rdd_reviews.ipynb))
    - Часть 2. Самостоятельное прилоожение ([Java](docs/spark_reviews.md) | [Python](docs/spark_reviews_py.md))
- [UDF в PySpark](/notebooks/spark_udf.ipynb)
- [Примеры применения Spark DataFrames](/notebooks/spark_gf_biketrips.ipynb)
- [Spark и Jupyter при помощи Livy в качестве REST-сервера  Spark](docs/spark_livy_jupyter.md)



## Spark Streaming



#### Практика:

Kafka:
- [Введение в распределенный брокер сообщений Kafka](docs/kafka_basics.md): Как настроить Kafka

DStreams (RDD API):

- [Введение в Spark Streaming](docs/spark_streaming_intro.md)<br>Преобразования без сохранения состояния, с сохранением состояния и оконные преобразования 
- [Spark Streaming при помощи Kafka](docs/spark_streaming_kafka.md)<br>Использование Kafka в качестве источника ввода для приложения Spark Streaming
- [Spark Streaming при помощи Kafka и Twitter API](docs/spark_streaming_kafka_tweets.md)<br>Использование producer Kafka с сообщениями, полученными от API Twitter, и приложения Spark Steaming, с Kafka Consumer в качестве источника ввода для обработки твитов
- [Классификация спама, используя Sklearn и Spark Streaming](docs/spark_streaming_classifier.md)<br>Использование модели классификации спама, созданной с помощью библиотеки sklearn, в приложении Spark Streaming.
- [Обновляемая трансляция в приложении Spark Streaming](docs/spark_streaming_update.md)<br>Как использовать модели машинного обучения, которые периодически меняются, в приложениях Spark Streaming
- [Веб-сервис при помощи Spark Streaming и Kafka](docs/spark_streaming_service.md)
<!--[Introduction to Spark Streaming](docs/spark_streaming.md)-->

Structured Streaming (DataFrame API):
- [Выполнение и обновление режимов вывода](docs/spark_streaming_structured_output_modes.md)
- [Как включить метку времени](docs/spark_streaming_structured_append_timestamp.md)
- [Окно с добавлением режима вывода](docs/spark_streaming_structured_window_append.md)



## Spark MLlib

#### Практика:

RDD API:

- [Регрессия, классификация и кластеризация и Spark](notebooks/spark_rdd_ml_basics.ipynb)
- [Классификация текстовых документов в Spark](notebooks/spark_rdd_ml_spam_classification.ipynb)

DataFrame API:

- [Boston House Price и Spark MLlib](notebooks/spark_df_price_regression_cv.ipynb)
- [Multiclass Text Document Classification using Spark](notebooks/spark_df_docclass.ipynb)
- Recommendation Systems:
    - [Факторизация матрицы рейтингов и Spark MLlib](notebooks/spark_df_movie_recommendation.ipynb)
    - [Item-based collaborative filtering](lib/python/recommend/itemrecom.py) (python module)
- [Комбинация решающих деревьев и Spark MLlib](notebooks/spark_df_purchase_tree.ipynb)

Extra topics:

- [Spark and sklearn models](notebooks/spark_df_sklearn.ipynb)
- [Image Recognition using SynapseML](notebooks/spark_synapseml.ipynb)


## Spark GraphFrame

#### Практика:

- [Introduction to Graph Analysis with Spark GraphFrames](notebooks/spark_gf_airplanes.ipynb)


## Spark в Docker

#### Практика:

- [Install Docker and Docker-Compose](docs/howto_install_docker.md)
- [Deploying Spark on YARN cluster using Docker](docs/spark_docker.md)


## Spark on Kubernetes

#### Практика:

- [Spark Standalone Cluster on Kubernetes using Deployments](docs/spark_k8s_deployment.md)
- [Spark on Kubernetes: spark-submit](docs/spark_k8s_spark-submit.md)
