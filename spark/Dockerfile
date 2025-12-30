FROM apache/spark:3.5.1-python3

USER root
WORKDIR /app

# Variables Python pour PySpark
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Installer les dépendances Python
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    scikit-learn \
    kafka-python \
    joblib

# Copier le consumer
COPY consumer.py /app/consumer.py

# ⚠️ IMPORTANT : chemin ABSOLU vers spark-submit
CMD ["/opt/spark/bin/spark-submit","--packages","org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1", "/app/consumer.py"]
