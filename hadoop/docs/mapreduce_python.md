# MapReduce и Python
Усовик С.В. (usovik@bmstu.ru)

## Разделы:

- Требования
- Конфигурация
- Установка плагина `Python` для `IntelliJ`
- Создание `Python`-проекта
- Простой исходный код
- Запуск MapReduce с локальными файлами
- Запуск MapReduce `python`-приложения на кластере YARN
- Рекомендации

## Требования

Для запуска необходима установка следующего ПО:

- Install Ubuntu 14+ (with Python 3.x)
- Install Java 8
- Download Hadoop 3+
- (Optional) Install IntelliJ 2019+ (for Python code)
- (Optional) Install PyCharm 2019+ (for Python code)
- (Optional) Install Jupyter Notebook

## Установка плагина`Python` для `IntelliJ`

`File` -> `Settings` -> `Plugins` -> Найти плагин `Python Community Edition` от `JetBrains` -> Выбрать `Install` -> Перезапустить IDE

## Создание `Python`-проекта

`File` -> `New` -> `Project...` -> `Python` -> Next ->  Name: `wordcountapp` - > Finish

## Простой `исходный код`

Mapper

[tokenizer_mapper.py](../projects/py/wordcountapp/tokenizer_mapper.py)

Combiner/Reducer

[intsum_reducer.py](../projects/py/wordcountapp/intsum_reducer.py)

## Запуск MapReduce слокальными файлами

Запустите mapper с небольшим текстовым файлом и посмотрите на результат:

`cat /PATH/data/samples.json | python tokenizer_mapper.py`

Вход reducer должен быть сортирован. Так, `hadoop-streaming` сортирует кортежи из результатов map-задач по ключу.

`cat /PATH/data/samples.json | python tokenizer_mapper.py | sort`

Запуск полного конвеера map-reduce:

`cat /PATH/data/samples.json | python tokenizer_mapper.py | sort | python intsum_reducer.py`

## Запуск MapReduce `python`-приложения на кластере YARN

```
yarn jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.1.2.jar \
    -D mapreduce.job.reduces=2 \
    -mapper "python /PATH/py/wordcountapp/tokenizer_mapper.py/tokenizer_mapper.py" \
    -reducer "python /PATH/py/wordcountapp/intsum_reducer.py" \
    -input "/data/yarn/reviews_Electronics_5_2.json" \
    -output "/data/yarn/output"
```