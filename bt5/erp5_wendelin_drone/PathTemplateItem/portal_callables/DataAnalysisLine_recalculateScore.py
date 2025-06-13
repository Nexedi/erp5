import math
import pandas as pd


# Take the data from the score list array. See if the array is larger than this one. If it is not, do not do anything. Else recalculate the scores for each simulation we have seen (just sort the data).
# Now, to save space, we just overwrite the old array with the new one, that contains the new scores
# This new array will give us the final overview of the ranking of the parameters. This can be used by our genetic algorithm to decide when we can stop and which parameters worked the best.




new_score_dtypes= [
  ('name', 'S256'),
  ('Param1', 'f8'),
  ('Param2', 'f8'),
  ('distance_reciprocal', 'f8'),
  ('ASML_reciprocal', 'f8'),
  ('ground_speed_reciprocal', 'f8'),
  ('climb_rate_reciprocal', 'f8'),
  ('score_reciprocal', 'f8'),
  ('score_cosine_row', 'f8'),
  ('score_cosine_column', 'f8'),
  ('iteration', 'i8')
]


new_plot_dtypes = [
  ('Param1', 'f8'),
  ('Param2', 'f8'),
  ('timestamp', 'f8'),
  ('distance_diff', 'f8'),
  ('ASML_diff', 'f8'),
  ('ground_speed_diff', 'f8'),
  ('climb_rate_diff', 'f8'),
  ('distance_reciprocal', 'f8'),
  ('ASML_reciprocal', 'f8'),
  ('ground_speed_reciprocal', 'f8'),
  ('climb_rate_reciprocal', 'f8'),
  ('score_reciprocal', 'f8'),
  ('score_cosine_row', 'f8'),
  ('score_cosine_column', 'f8'),
  ('iteration', 'i8')
]


score_array = input_array_scores["Data Array"]
new_score_array = out_array_scores["Data Array"]

plot_array = input_array_plot["Data Array"]
new_plot_array = out_array_plots["Data Array"]

# Should only look at the newest few
score_nparray = score_array.getArray()
if score_nparray is None:
  score_nparray = out_array_scores["Data Array"].initArray(shape=(0,), dtype=new_score_dtypes)

plot_nparray = plot_array.getArray()
if plot_nparray is None:
  plot_nparray = out_array_plots["Data Array"].initArray(shape=(0,), dtype=new_plot_dtypes)
  
old_score_df = pd.DataFrame.from_records(score_nparray[:].copy())
old_plot_df = pd.DataFrame.from_records(plot_nparray[:].copy())

progress_indicator = input_array_scores["Progress Indicator"]
seen_sims = progress_indicator.getStringOffsetIndex()

if seen_sims is None:
  seen_sims = ""
  
sim_flight_names = list(old_score_df["name"])
  
# We will only continue if there is new data available.
if len([x for x in sim_flight_names if x not in seen_sims]) == 0: 
  return 









new_score_nparray = new_score_array.getArray()
if new_score_nparray is None:
  new_score_nparray = out_array_scores["Data Array"].initArray(shape=(0,), dtype=new_score_dtypes)



new_plot_nparray = new_plot_array.getArray()
if new_plot_nparray is None:
  new_plot_nparray = out_array_plots["Data Array"].initArray(shape=(0,), dtype=new_plot_dtypes)




new_score_df = pd.DataFrame.from_records(new_score_nparray[:].copy())

new_plot_df = pd.DataFrame.from_records(new_plot_nparray[:].copy())







new_score_iteration = new_score_df["iteration"].max()
if math.isnan(new_score_iteration):
  new_score_iteration = 0


new_score_df = new_score_df.drop(["iteration"],axis=1)


new_plot_iteration = new_plot_df["iteration"].max()
if math.isnan(new_plot_iteration):
  new_plot_iteration = 0

#new_plot_df = new_plot_df.drop(columns=["iteration"])


answer_scores = pd.concat([old_score_df, new_score_df]).drop_duplicates(subset=['Param1','Param2'], keep='last')
answer_plots = pd.concat([old_plot_df, new_plot_df]).drop_duplicates(subset=['Param1','Param2'], keep='last')

answer_scores["score_reciprocal"] = answer_scores["score_reciprocal"].astype('float64')



answer_scores = answer_scores.nlargest(5, "score_reciprocal")
answer_plots = old_plot_df[old_plot_df["name"].isin(list(answer_scores["name"]))]





new_score_iteration = new_score_iteration + 1
new_plot_iteration = new_plot_iteration + 1

answer_scores["iteration"] = new_score_iteration
answer_plots["iteration"] = new_plot_iteration

# We will remove all the data from the data arrays before we append the new data. Essentially we will be left with only the best few iterations
new_score_nparray = out_array_scores["Data Array"].initArray(shape=(0,), dtype=new_score_dtypes)

new_plot_nparray = out_array_plots["Data Array"].initArray(shape=(0,), dtype=new_plot_dtypes)

new_score_nparray.append(answer_scores.to_records(index = False))











# Group the DataFrame by the 'name' column
grouped = answer_plots.groupby(['Param1', 'Param2'])

# Initialize a list to store the resulting DataFrames
resulting_dfs = []



# Iterate over unique names and create DataFrames
for name, group in grouped:
  resulting_dfs.append(group)


current_idx = 0

current_rank = 1
for df in resulting_dfs:
  df = df.drop(["name"], axis=1)
  data_array_line_plot = out_array_plots["Data Array"].get(str(current_rank))
  df = df.drop_duplicates()
  new_plot_nparray.append(df.to_records(index = False))

  if data_array_line_plot is None:
    data_array_line_plot = out_array_plots["Data Array"].newContent(id=current_rank,
                                               portal_type="Data Array Line")

  data_array_line_plot.edit(
  reference=current_rank,
     index_expression="%s:%s" %(current_idx, new_plot_nparray.shape[0])
    )
  current_idx = new_plot_nparray.shape[0]
  current_rank = current_rank + 1


progress_indicator.setStringOffsetIndex(sim_flight_names)
    
return
