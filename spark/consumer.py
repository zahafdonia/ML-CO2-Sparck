import os
import json
import joblib
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, DoubleType, BooleanType
from pyspark.ml.feature import VectorAssembler
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_squared_error

# ================= CONFIG =================
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "streaming_data"

MODEL_PATH = "/models/sgd.joblib"
METRICS_PATH = "/models/metrics.json"

os.makedirs("/models", exist_ok=True)

# ================= SPARK ==================
spark = SparkSession.builder \
    .appName("VehicleFuelConsumptionRegression") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoints") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ================= SCHEMA =================
schema = StructType([
    StructField("Engine_Size", DoubleType()),
    StructField("Cylinders", DoubleType()),
    StructField("Fuel_Consumption_City", DoubleType()),
    StructField("Fuel_Consumption_Hwy", DoubleType()),
    StructField("Fuel_Consumption_Comb", DoubleType()),
    StructField("CO2_Emissions", DoubleType()),
    StructField("Fuel_Type_D", BooleanType()),
    StructField("Fuel_Type_E", BooleanType()),
    StructField("Fuel_Type_N", BooleanType()),
    StructField("Fuel_Type_X", BooleanType()),
    StructField("Fuel_Type_Z", BooleanType())
])

# ================= MODEL ==================
if os.path.exists(MODEL_PATH):
    print("✅ Loading existing model")
    model = joblib.load(MODEL_PATH)
else:
    print("🆕 Initializing new SGDRegressor")
    model = SGDRegressor(max_iter=1000, tol=1e-3)

if os.path.exists(METRICS_PATH):
    with open(METRICS_PATH) as f:
        metrics = json.load(f)
else:
    metrics = {"batch": [], "rmse": []}

# ================= STREAM =================
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .load()

parsed_df = raw_df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

feature_cols = [
    "Engine_Size", "Cylinders",
    "Fuel_Consumption_City",
    "Fuel_Consumption_Hwy",
    "Fuel_Consumption_Comb",
    "Fuel_Type_D", "Fuel_Type_E",
    "Fuel_Type_N", "Fuel_Type_X",
    "Fuel_Type_Z"
]

assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

train_df = assembler.transform(parsed_df.dropna()).select(
    "features",
    col("CO2_Emissions").alias("label")
)

# ================= TRAIN ==================
def incremental_train(batch_df, batch_id):
    global model, metrics

    pdf = batch_df.toPandas()
    if pdf.empty:
        print(f"⚠️ Batch {batch_id} empty")
        return

    X = np.vstack(pdf["features"].apply(lambda x: x.toArray()))
    y = pdf["label"].values

    model.partial_fit(X, y)

    preds = model.predict(X)
    rmse = mean_squared_error(y, preds, squared=False)

    metrics["batch"].append(batch_id)
    metrics["rmse"].append(float(rmse))

    # ✅ Écriture atomique des métriques
    tmp_metrics = METRICS_PATH + ".tmp"
    with open(tmp_metrics, "w") as f:
        json.dump(metrics, f)
    os.replace(tmp_metrics, METRICS_PATH)

    # ✅ Sauvegarde du modèle
    joblib.dump(model, MODEL_PATH)

    print(f"✅ Batch {batch_id} | RMSE = {rmse:.4f}")

query = train_df.writeStream \
    .foreachBatch(incremental_train) \
    .start()

query.awaitTermination()
