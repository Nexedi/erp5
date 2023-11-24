import math
import pandas as pd
import numpy as np
import re



R = 6371e3

def cosine_custom(df1, df2):
  return df1.dot(df2) / ((np.sqrt(np.square(df1).sum())) * np.sqrt(np.square(df2).sum()))

def mean_cosine_similarity_custom(df1, df2):
  cosine_similarity_sum = 0
  for column in df1.columns:
    cosine_similarity_sum += cosine_custom(df1[column], df2[column])
  return cosine_similarity_sum/len(df1.columns)

def mean_operation(data):
  return float(sum(data)/len(data))


def distance(lat1, lon1, lat2, lon2):
  lat1_rad = lat1 * math.pi / 180
  lat2_rad = lat2 * math.pi / 180
  lon1_rad = lon1 * math.pi / 180
  lon2_rad = lon2 * math.pi / 180
  haversine_phi = math.sin((lat2_rad - lat1_rad) / 2) ** 2
  sin_lon = math.sin((lon2_rad - lon1_rad) / 2)
  h = haversine_phi + math.cos(lat1_rad) * math.cos(lat2_rad) * sin_lon * sin_lon
  return 2 * R * math.sin(math.sqrt(h))

def rated_value(next_value, previous_value, rate):
  if rate > 0.5:
    return next_value - (next_value - previous_value) * (1 - rate)
  else:
    return previous_value + (next_value - previous_value) * rate






real_array = input_array_real["Data Array"]
sim_array = input_array_sim["Data Array"]



real_flight_names = list(real_array)
sim_flight_names = list(sim_array)
if len(real_flight_names) == 0:
  context.log("The real flight data is still missing")
  return
nparray = real_array.get(real_flight_names[0])

nparray_real = nparray.getArray()
real_flight = pd.DataFrame(data=nparray_real, columns=["timestamp (ms)","latitude ()","longitude ()","AMSL (m)","rel altitude (m)","yaw ()","ground speed (m/s)","climb rate (m/s)"])



progress_indicator_sim = input_array_sim["Progress Indicator"]


seen_sims = progress_indicator_sim.getStringOffsetIndex()
new_seen = ""
if seen_sims is None:
  seen_sims = ""
  score_dtypes = {'name': 'S256', 'Param1': 'f16', 'Param2': 'f16', 
          'distance_reciprocal': 'f8', 'ASML_reciprocal': 'f8', 
          'ground_speed_reciprocal': 'f8', 'climb_rate_reciprocal': 'f8', 
          'score_reciprocal': 'f16', 'score_cosine_row': 'f16', 
          'score_cosine_column': 'f16'}

  _ = out_array_scores["Data Array"].initArray(shape=(0,), dtype=list(score_dtypes.items()))

  plot_dtypes = {
    'name': 'S256',
    'Param1': 'f8',
    'Param2': 'f8',
    'timestamp': 'f8',
    'distance_diff': 'f8',
    'ASML_diff': 'f8',
    'ground_speed_diff': 'f8',
    'climb_rate_diff': 'f8',
    'distance_reciprocal': 'f8',
    'ASML_reciprocal': 'f8',
    'ground_speed_reciprocal': 'f8',
    'climb_rate_reciprocal': 'f8',
    'score_reciprocal': 'f16',
    'score_cosine_row': 'f16',
    'score_cosine_column': 'f16'
  }
  _ = out_array_plot_data["Data Array"].initArray(shape=(0,), dtype=list(plot_dtypes.items()))

simulated_flight_list = []
simulated_flights_value_dict_list = []
selected_simulation_data_dict_list = []
if len([x for x in sim_flight_names if x not in seen_sims]) == 0:
  return




not_seen_list = [x for x in sim_flight_names if x not in seen_sims]
for name in not_seen_list[:]:
  if name[:14] == 'simulation_log':
    splitted_filename = name[:-4].split('_')
    distance_list_tuple = ([],[], [], [], []) 
    nparray = sim_array.get(name)
    nparray_sim = nparray.getArray()
    simulated_flight = pd.DataFrame(data=nparray_sim, columns=["timestamp (ms)","latitude ()","longitude ()","AMSL (m)","rel altitude (m)","yaw ()","ground speed (m/s)","climb rate (m/s)"])
    simulated_flight = simulated_flight.applymap(lambda value: np.format_float_scientific(float(value)) if isinstance(value, str) and 'e' in value else value)
    simulated_flight_list.append(simulated_flight)
    max_simulator_timestamp = simulated_flight["timestamp (ms)"].max()
    min_simulator_timestamp = simulated_flight["timestamp (ms)"].min()
    
    
    tmp_sim = {
    'longitude': [],
    'latitude': [],
    'asml': [],
    'ground_speed': [],
    'climb_rate': []
    }
    tmp_real = {
    'longitude': [],
    'latitude': [],
    'asml': [],
    'ground_speed': [],
    'climb_rate': []
    }
    
    for idx, row in real_flight.iterrows():
      if max_simulator_timestamp < row["timestamp (ms)"]:
        break
      if min_simulator_timestamp > row["timestamp (ms)"]:
        continue
      over_timestamp = simulated_flight[simulated_flight["timestamp (ms)"] >= row["timestamp (ms)"]].head(1)
      under_timestamp = simulated_flight[simulated_flight["timestamp (ms)"] <= row["timestamp (ms)"]].tail(1)
      
      if (float(over_timestamp["timestamp (ms)"]) - float(under_timestamp["timestamp (ms)"])) == 0:
        rate = 0
      else:
        rate = (float(over_timestamp["timestamp (ms)"]) - row["timestamp (ms)"])/(float(over_timestamp["timestamp (ms)"]) - float(under_timestamp["timestamp (ms)"]))

      tmp_sim["latitude"].append(rated_value(float(over_timestamp["latitude ()"]), float(under_timestamp["latitude ()"]), rate)) 
      tmp_sim["longitude"].append(rated_value(float(over_timestamp["longitude ()"]), float(under_timestamp["longitude ()"]), rate))
      tmp_sim["asml"].append(rated_value(float(over_timestamp["AMSL (m)"]), float(under_timestamp["AMSL (m)"]), rate))
      tmp_sim["ground_speed"].append(rated_value(float(over_timestamp["ground speed (m/s)"]), float(under_timestamp["ground speed (m/s)"]), rate))
      tmp_sim["climb_rate"].append(rated_value(float(over_timestamp["climb rate (m/s)"]), float(under_timestamp["climb rate (m/s)"]), rate))  
      tmp_real["latitude"].append(row["latitude ()"])
      tmp_real["longitude"].append(row["longitude ()"])
      tmp_real["asml"].append(row["AMSL (m)"])
      tmp_real["ground_speed"].append(row["ground speed (m/s)"])
      tmp_real["climb_rate"].append(row["climb rate (m/s)"])

      for index, value in enumerate((
            row["timestamp (ms)"] / 1000,
            distance(
                row["latitude ()"],
                row["longitude ()"],
                rated_value(float(over_timestamp["latitude ()"]), float(under_timestamp["latitude ()"]), rate),
                rated_value(float(over_timestamp["longitude ()"]), float(under_timestamp["longitude ()"]), rate),
            ),
            rated_value(float(over_timestamp["AMSL (m)"]), float(under_timestamp["AMSL (m)"]), rate) - row["AMSL (m)"],
            rated_value(float(over_timestamp["ground speed (m/s)"]), float(under_timestamp["ground speed (m/s)"]), rate) - row["ground speed (m/s)"],
            rated_value(float(over_timestamp["climb rate (m/s)"]), float(under_timestamp["climb rate (m/s)"]), rate) - row["climb rate (m/s)"]
        )):

        distance_list_tuple[index].append(value)
        # If we have at least 100 entries (timestamps) analysed, add the filename to the list

    # If there is some data, continue (before we needed at least 100 datapoints, which is fair)
    if len(distance_list_tuple[0]) > 0:
      # Add it to the dictionary
      # A list of simulations, and their values over time
      pattern = r'\((.*?)\)'
      match = re.search(pattern, name)
      if match:
        values_str = match.group(1)
        parameters = [float(val.strip()) for val in values_str.split(',')]
        
      reciprocal_of_difference = [1/(1+mean_operation(list(map(abs, x)))) for x in distance_list_tuple[1:]]
      score_reciprocal = sum(reciprocal_of_difference)

      tmp_df_sim = pd.DataFrame(tmp_sim)
      tmp_df_real = pd.DataFrame(tmp_real)
      # Uncomment once you can actually use np..norm
      score_cosine_row =mean_cosine_similarity_custom(tmp_df_real, tmp_df_sim)# cosine_similarity_rows(tmp_df_real, tmp_df_sim).mean()
      score_cosine_column = mean_cosine_similarity_custom(tmp_df_real.T, tmp_df_sim.T)#cosine_similarity_rows(tmp_df_real.T, tmp_df_sim.T).mean()

      simulated_flights_value_dict_list.append({
            "name": name,
            "Param1" : parameters[0],
            "Param2": parameters[1],
            "timestamp": distance_list_tuple[0],
            "distance_diff": distance_list_tuple[1],
            "ASML_diff" : distance_list_tuple[2],
            "ground_speed_diff" : distance_list_tuple[3],
            "climb_rate_diff" : distance_list_tuple[4],
            "distance_reciprocal": reciprocal_of_difference[0],
            "ASML_reciprocal" : reciprocal_of_difference[1],
            "ground_speed_reciprocal" : reciprocal_of_difference[2],
            "climb_rate_reciprocal" : reciprocal_of_difference[3],
            "score_reciprocal": score_reciprocal/4,
            "score_cosine_row" : score_cosine_row,
            "score_cosine_column" : score_cosine_column
        })

      selected_simulation_data_dict_list.append({
            "name": name,
            "Param1" : parameters[0],
            "Param2": parameters[1],
            "distance_reciprocal": reciprocal_of_difference[0],
            "ASML_reciprocal" : reciprocal_of_difference[1],
            "ground_speed_reciprocal" : reciprocal_of_difference[2],
            "climb_rate_reciprocal" : reciprocal_of_difference[3],
            "score_reciprocal": score_reciprocal/4,
            "score_cosine_row" : score_cosine_row,
            "score_cosine_column" : score_cosine_column
        })


combined_data = pd.DataFrame()  # Initialize an empty DataFrame

# Iterate through the list of dictionaries
for data_dict in simulated_flights_value_dict_list:
    tmp = pd.DataFrame(data_dict)  # Wrap data_dict in a list and create a DataFrame
    combined_data = pd.concat([combined_data, tmp], ignore_index=True)



plot_dtypes = {
    'name': 'S256',
    'Param1': 'float64',
    'Param2': 'float64',
    'timestamp': 'float64',
    'distance_diff': 'float64',
    'ASML_diff': 'float64',
    'ground_speed_diff': 'float64',
    'climb_rate_diff': 'float64',
    'distance_reciprocal': 'float64',
    'ASML_reciprocal': 'float64',
    'ground_speed_reciprocal': 'float64',
    'climb_rate_reciprocal': 'float64',
    'score_reciprocal': 'float64',  
    'score_cosine_row': 'float64',  
    'score_cosine_column': 'float64', 
}


plots_df = combined_data
if plots_df.empty:
  context.log("The file names are not correct or no data")
  return

plots_df=plots_df.astype(plot_dtypes)


# Initialize a dictionary to store the combined values
combined_data = {}

# Iterate through the list of dictionaries
for data_dict in selected_simulation_data_dict_list:
  for key, value in data_dict.items():
    # Initialize a list for the key if it doesn't exist
    if key not in combined_data:
      combined_data[key] = []
        
    # Append the value to the list
    combined_data[key].append(value)



score_dtypes = {'name': 'S256', 'Param1': 'float64', 'Param2': 'float64', 
          'distance_reciprocal': 'float64', 'ASML_reciprocal': 'float64', 
          'ground_speed_reciprocal': 'float64', 'climb_rate_reciprocal': 'float64', 
          'score_reciprocal': 'float64', 'score_cosine_row': 'float64', 
          'score_cosine_column': 'float64'}
scores_df = pd.DataFrame(combined_data)
scores_df = scores_df.astype(score_dtypes)
###############################



zbigarray_scores = out_array_scores["Data Array"].getArray()

score_names = list(out_array_scores["Data Array"])





scores_ndarray = scores_df.to_records(index = False)
scores_ndarray = scores_ndarray.astype([("name", "S256"),("Param1", "f8"), ("Param2", "f8"), ("distance_reciprocal", "f8"), ("ASML_reciprocal", "f8"), ("ground_speed_reciprocal", "f8"), ('climb_rate_reciprocal', 'f8'), ("score_reciprocal", "f8"), ("score_cosine_column", "f8"), ("score_cosine_row", "f8")])


if zbigarray_scores is None:
  zbigarray_scores = out_array_scores["Data Array"].initArray(shape=(0,), dtype=scores_ndarray.dtype.fields)

score_array_start_idx = zbigarray_scores.shape[0]

zbigarray_scores.append(scores_ndarray)



new_key = "Iteration_1"
try:
  max_nr = 0
  for key in score_names:
    old_key_nr = int(key.split("_")[-1])
    if old_key_nr>max_nr:
      max_nr=old_key_nr
    new_key = "Iteration_" + str(max_nr+1)
except:
  new_key = "Iteration_1"





data_array_line_score = out_array_scores.get(new_key)

if data_array_line_score is None:
  data_array_line_score = out_array_scores["Data Array"].newContent(id=new_key,
                                             portal_type="Data Array Line")

data_array_line_score.edit(reference=new_key,
     index_expression="%s:%s" %(score_array_start_idx, zbigarray_scores.shape[0])
  )

##########################


zbigarray_plots = out_array_plot_data["Data Array"].getArray()







plots_ndarray = plots_df.to_records(index = False)
plots_ndarray = plots_ndarray.astype([('name', 'S256'), ('Param1', 'f8'), ('Param2', 'f8'), ('timestamp', 'f8'), ('distance_diff', 'f8'), ('ASML_diff', 'f8'), ('ground_speed_diff', 'f8'), ('climb_rate_diff', 'f8'), ('distance_reciprocal', 'f8'), ('ASML_reciprocal', 'f8'), ('ground_speed_reciprocal', 'f8'), ('climb_rate_reciprocal', 'f8'), ('score_reciprocal', 'f8'), ('score_cosine_row', 'f8'), ('score_cosine_column', 'f8')])

if zbigarray_plots is None:
  zbigarray_plots = out_array_plot_data["Data Array"].initArray(shape=(0,), dtype=plots_ndarray.dtype.fields)


plot_array_start_idx = zbigarray_plots.shape[0]

zbigarray_plots.append(plots_ndarray)



new_key_plot = "PlotIteration_1"
plot_names = list(out_array_plot_data["Data Array"])

try:

  max_nr = 0
  for key in plot_names:
    old_key_nr = int(key.split("_")[1])
    if old_key_nr>max_nr:
      max_nr=old_key_nr
    new_key_plot = "PlotIteration_" + str(max_nr+1)

except:
  new_key_plot = "PlotIteration_1"





data_array_line_plot = out_array_plot_data.get(new_key_plot)

if data_array_line_plot is None:
  data_array_line_plot = out_array_plot_data["Data Array"].newContent(id=new_key_plot,
                                             portal_type="Data Array Line")

data_array_line_plot.edit(reference=new_key_plot,
     index_expression="%s:%s" %(plot_array_start_idx, zbigarray_plots.shape[0])
  )
new_seen_sims = "".join([x for x in sim_flight_names if x not in seen_sims])
new_seen_sims = new_seen_sims + seen_sims

progress_indicator_sim.setStringOffsetIndex(new_seen_sims)
