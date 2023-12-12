#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module uses pandasai and streamlit to produce a web-based app with data
visualizations for a brain artery network dataset
"""
import os
import time
import pdb
import requests
import pandas as pd
import streamlit as st
from pandasai import SmartDataframe
from pandasai.llm import OpenAI

from bava.api.database import BavaDB
from bava.api.config import FAST_API_URL
from bava.visualization3d.subject_graph import SubjectGraph

st.set_option('deprecation.showPyplotGlobalUse', False)

def page_pandasai():
	"""
	Produces the text input for the pandasai feature of the app. Users enter their
	prompt directly and then pandasai uploads the corresponding visualization.

	"""
	
	secret_values = os.environ['OPENAI_API_KEY'] #use the command 'export OPENAI_API_KEY={your API key}' 
	llm = OpenAI(api_token=secret_values)
 
	st.title("Hi, I'm BAVA AI!" + "\nHow can I help you today?")
 
	# st.title('Data Summary')
	bava_db_dict = requests.get(url=f"{FAST_API_URL}/subjects/").json()
	bava_db = BavaDB(**bava_db_dict)
 
	# Create a multiselect for different datasets
	# the dataset names are from bava_db.subjects[i]['ID'].split('_')[0]
	dataset_options = list(set([subject['ID'].split('_')[0] for subject in bava_db.subjects]))
	selected_datasets = st.sidebar.multiselect('Datasets', dataset_options, default=dataset_options)
 
	# Create a filter bar for age
	age_info = bava_db.metadata.age
	min_age, max_age = st.sidebar.slider('Age Range', age_info.min, age_info.max, (age_info.min, age_info.max))

	# Create a filter bar for SBP
	sbp_info = bava_db.metadata.sbp
	min_sbp, max_sbp = st.sidebar.slider('SBP Range', sbp_info.min, sbp_info.max, (sbp_info.min, sbp_info.max))

	# Create a filter bar for DBP
	dbp_info = bava_db.metadata.dbp
	min_dbp, max_dbp = st.sidebar.slider('DBP Range', dbp_info.min, dbp_info.max, (dbp_info.min, dbp_info.max))
 
	# Create a filter bar for HDL
	hdl_info = bava_db.metadata.hdl
	min_hdl, max_hdl = st.sidebar.slider('HDL Range', hdl_info.min, hdl_info.max, (hdl_info.min, hdl_info.max))
 
	# Create a filter bar for LDL
	ldl_info = bava_db.metadata.ldl
	min_ldl, max_ldl = st.sidebar.slider('LDL Range', ldl_info.min, ldl_info.max, (ldl_info.min, ldl_info.max))

	# Create a filter bar for TC
	tc_info = bava_db.metadata.tc
	min_tc, max_tc = st.sidebar.slider('Total cholestral Range', tc_info.min, tc_info.max, (tc_info.min, tc_info.max))

	# Create a filter bar for TG
	tg_info = bava_db.metadata.tg
	min_tg, max_tg = st.sidebar.slider('TG Range', tg_info.min, tg_info.max, (tg_info.min, tg_info.max))

	# Create a filter bar for Framingham score
	framingham_info = bava_db.metadata.framingham_risk
	min_framingham, max_framingham = st.sidebar.slider('Framingham Risk Score Range', framingham_info.min, framingham_info.max, (framingham_info.min, framingham_info.max))

	# Create a selectbox for diabetes
	diabetes_options = ['Have Diabetes', "Don't Have Diabetes", 'All']
	diabetes_choice = st.sidebar.selectbox('Diabetes', diabetes_options, index=2)  # Set the default index to 2 for 'All'
	diabetes_option = None

	if diabetes_choice == 'Have Diabetes':
		diabetes_option = True
	elif diabetes_choice == "Don't Have Diabetes":
		diabetes_option = False
	else:
		diabetes_option = None

	# Create a selectbox for hypertension
	hypertension_options = ['Have Hypertension', "Don't Have Hypertension", 'All']
	hypertension_choice = st.sidebar.selectbox('Hypertension', hypertension_options, index=2)  # Set the default index to 2 for 'All'
	hypertension_option = None

	if hypertension_choice == 'Have Hypertension':
		hypertension_option = True
	elif hypertension_choice == "Don't Have Hypertension":
		hypertension_option = False
	else:
		hypertension_option = None

	# Create multiselect for gender
	gender_options = ['Male', 'Female']
	gender_values = [1, 0]
	selected_genders = st.sidebar.multiselect('Gender', gender_options, default=gender_options)
 
	# Map the selected gender to their corresponding values
	selected_gender_values = [gender_values[gender_options.index(gender)] for gender in selected_genders]

	# Create checkboxes for race
	race_options = ['Native American', 'Pacific Islander', 'Asian', 'Caucasian', 'African American', 'Multiple Races', 'Other']
	race_values = [1, 2, 3, 4, 5, 6, 7]
	selected_races = st.sidebar.multiselect('Race', race_options, default=race_options)

	# Map the selected races to their corresponding values
	selected_race_values = [race_values[race_options.index(race)] for race in selected_races]

	filter_options = {
		"datasets": selected_datasets if selected_datasets else dataset_options,
		"age": (min_age, max_age),
		"sbp": (min_sbp, max_sbp),
		"dbp": (min_dbp, max_dbp),
		"hdl": (min_hdl, max_hdl),
		"ldl": (min_ldl, max_ldl),
		"tc": (min_tc, max_tc),
		"tg": (min_tg, max_tg),
		"framingham_risk": (min_framingham, max_framingham),
		"diabetes": diabetes_option,
		"hypertension": hypertension_option,
		"genders": selected_gender_values if selected_gender_values else gender_values,
  		"race": selected_race_values if selected_race_values else race_values,}

	filtered_subjects = requests.post(url=f"{FAST_API_URL}/filter/", json=filter_options).json()
	if not filtered_subjects:
		st.markdown("No records found for applied filters! Please update your filters.")
	
	else:
		st.markdown(f"{len(filtered_subjects)} records found!")
		# create an empty list
		features = []
		for subject in filtered_subjects:
			# print the index of the current subject among all the subjects, and the loading time
			subject_id = subject['ID']
   
			selected_subject = requests.get(url=f"{FAST_API_URL}/subjects/{subject_id}").json()
			unstructured_data = selected_subject.pop("unstructured_data")
   
			# check if unsturctured_data is None
			if unstructured_data is None:
				continue

			# print(f"Loading subject {filtered_subjects.index(subject) + 1} of {len(filtered_subjects)}")

			# retrieve the subject graph and get the morphological features and graph features
			subject_graph = SubjectGraph(unstructured_data)
			graph_features = subject_graph.graph_features # save time by not using graph features
			morphological_features = subject_graph.morphological_features
			# concat the graph features and morphological features with the subject
			selected_subject.update(graph_features)
			selected_subject.update(morphological_features)
			features.append(selected_subject)
   	
    # convert of list of dictionaries to a dataframe
	df = pd.DataFrame(features)
	# replace the NaN values with 0
	df = df.fillna(0)
 
	smart_df = SmartDataframe(df, config={"llm": llm,"enable_cache": False,"save_charts": False,},)
   
	with st.form("Question"):
		question = st.text_input("Message BAVA AI below. For example, type 'Plot the average SBP across different age groups'.", value="", type="default")
		question_sent = st.form_submit_button("Send")
		if question_sent:
			with st.spinner():
				ai_output = smart_df.chat(question)

				if ai_output is not None:
					st.write(str(ai_output))
				else:
					st.pyplot(ai_output)
					st.write("Data visualization shared!")

	# Add a button at upper right corner to go back to the homepage
	if st.button('Back to Homepage'):
		st.balloons()
		st.stop()

# Run the Streamlit app
if __name__ == "__main__":
	page_pandasai()
	
