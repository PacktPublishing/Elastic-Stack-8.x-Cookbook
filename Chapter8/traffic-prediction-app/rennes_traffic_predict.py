import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

ES_CID = os.getenv('ES_CID')
ES_USER = os.getenv('ES_USER')
ES_PWD = os.getenv('ES_PWD')
INFERENCE_MODEL_ID = os.getenv('INFERENCE_MODEL_ID')

es = Elasticsearch(
    cloud_id=ES_CID,
    basic_auth=(ES_USER, ES_PWD)
)

es.info()

# Streamlit UI
st.set_page_config(page_title="Rennes Traffic Prediction", page_icon=":car:", layout="centered")

st.image(
    'resources/rennes-logo.png',
    width=250
)
st.header("Predict Traffic status in Rennes")

st.subheader("Enter location, time and speed data to predict the traffic status")

location = st.selectbox("Choose a location", ["16762", "1632", "1631", "16647_D", "15120", "13514"], help="Postal code of the location")
hour_of_day = st.selectbox("choose the hour of the day", ["01","02", "03", "04", "05","06", "07", "08", "09", "10", "12", "13", "14","15","16", "17", "18", "19", "20","21","22","23","00"], help="Hour of the Day")
day_of_week = st.selectbox("choose the day of the week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
# speed = st.text_input("Enter the maximum authorized speed", help="Enter the maximum authorized speed in km/h")
speed = st.select_slider("Enter the maximum authorized speed", options=[30, 50, 70, 80, 90, 110, 130], help="Enter the maximum authorized speed in km/h")

if st.button("Predict"):
    # create document
    docs = [
        {
            "_source": {
                "location_reference": location,
                "max_speed": {
                    "max": speed
                },
                "hour_of_day": hour_of_day,
                "day_of_week": day_of_week
            }
        }
    ]

    # Call simulate inference pipeline API with document
    response = es.ingest.simulate(docs=docs, id=INFERENCE_MODEL_ID)

    # get prediction
    prediction = response['docs'][0]['doc']['_source']['ml']['inference']['top_metrics']['traffic_status_prediction']['top_metrics.traffic_status_prediction']
    
    # get prediction probability
    prediction_probability = response['docs'][0]['doc']['_source']['ml']['inference']['top_metrics']['traffic_status_prediction']['prediction_probability']

    # display prediction
    st.markdown(""" #### Predicted traffic status: """ + prediction)
    st.info("Prediction probability: " + str(format(prediction_probability*100, '.2f')) + "%")
    with st.expander("View full response"):
        st.json(response.body)

