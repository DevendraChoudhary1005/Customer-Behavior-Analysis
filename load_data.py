import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

url = URL.create(
    "postgresql+psycopg2",
    username="postgres",
    password="DCdc@2005",
    host="localhost",
    port=5432,
    database="customer_behaviour",
)
engine = create_engine(url)

df = pd.read_csv("customer.csv")
df.to_sql("customer_shopping_behavior", engine, if_exists="replace", index=False, chunksize=1000, method="multi")

with engine.connect() as conn:
    print(conn.execute(text("SELECT COUNT(*) FROM customer_shopping_behavior")).scalar())