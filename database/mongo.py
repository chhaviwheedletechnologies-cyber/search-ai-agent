from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client=MongoClient(os.getenv("MONGO_URI"))
db=client[os.getenv("DB_NAME")]

businesses=db.businesses
fanouts=db.fanouts
ai_results=db.ai_results
citations=db.citations
visibility_scores=db.visibility_scores
recommendations=db.recommendations
execution_logs=db.execution_logs