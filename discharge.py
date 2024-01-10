import pandas as pd


# Full discharge calculation
def discharge_calculation(df_q, ratings_value, site_sql_id):
    # Calculate Discharge (Q) Offset
    # when re running this clears out old data
    if "comparison" in df_q.columns:
            df = df_q[["datetime", "data", "corrected_data", "observation_stage", "q_observation", "offset", "estimate", "comparison"]]
    if "comparison" not in df_q.columns:
            df = df_q[["datetime", "data", "corrected_data", "observation_stage", "q_observation", "offset", "estimate"]]

        # flag, if flag hasnt been set or has been reset get the rating
        # this should save processing speed
    rating_calculation_status = "not calculated"
    if rating_calculation_status != ratings_value:
            from rating import rating_calculator
            # fx sets flag and wont run unless flag has been reset
            rating_calculation_status, interpolate_discharge, interpolate_stage, gzf = rating_calculator(ratings_value, site_sql_id)
    # given this discharge you should have a stage of this
    df.loc[:, "rating_stage_for_observation"] = interpolate_stage(df['q_observation'])
    # so your stage is off by X
    df.loc[:, 'q_offset'] = df['rating_stage_for_observation'] - (df["corrected_data"]-gzf)
    # precent change
    df['rating_stage_for_observation'] = ((df['rating_stage_for_observation']-(df['observation_stage']-gzf))/df['rating_stage_for_observation'])*100
    df.rename(columns={'rating_stage_for_observation': "precent_q_change"}, inplace=True)
    # at your stage you should have a discharge of X
    # interpolate q_offset
    df.loc[:, 'discharge'] = df['q_offset']
    #df['discharge'] = df['q_offset']
    df['discharge'].interpolate(method='linear', inplace=True, axis=0, limit_direction='both')
    #df['stage_offset'] = (df['corrected_data']-gzf) + df['offset_interpolate']
    df['discharge'] = interpolate_discharge((df['corrected_data']-gzf) + df['discharge'])
    # if discharge is below rating it may return an na...right now we are filling this with zero but its not great
    df['discharge'] = df['discharge'].fillna(0)
    df["RatingNumber"] = ratings_value
    df['q_offset'] = round(df['q_offset'],2)
    df["precent_q_change"] = round(df["precent_q_change"],2)
    #df.to_csv(r"W:/STS/hydro/GAUGE/Temp/Ian's Temp/discharge_calc.csv")
    df.sort_values(by=['datetime'], inplace=True)
    #if "estimate" not in df.columns:
    #    df["estimate"] = 0

    if "comparison" in df.columns:
            df = df[["datetime", "data", "corrected_data", "discharge", "observation_stage", "q_observation", "offset", "q_offset", "precent_q_change", "RatingNumber", "estimate", "comparison"]]
    if "comparison" not in df.columns:
            df = df[["datetime", "data", "corrected_data", "discharge", "observation_stage", "q_observation", "offset", "q_offset", "precent_q_change", "RatingNumber", "estimate"]]
    return df


# finalize discharge dataframe
def finalize_discharge_dataframe(df_q):
    df_q['data'] = df_q['data'].round(2)
    df_q['corrected_data'] = df_q['corrected_data'].round(2)
    df_q['observation_stage'] = df_q['observation_stage'].round(2)
    df_q['q_observation'] = df_q['q_observation'].round(2)
    df_q['discharge'] = df_q['discharge'].round(2)
        # convert datetime
    df_q['datetime'] = pd.to_datetime(
            df_q['datetime'], format='%Y-%m-%d %H:%M:%S', errors='coerce', infer_datetime_format=True)
    if "comparison" in df_q.columns:
            df_q = df_q[["datetime", "data", "corrected_data", "discharge", "observation_stage", "q_observation", "offset", "q_offset", "precent_q_change", "RatingNumber", "estimate", "comparison"]]
    if "comparison" not in df_q.columns:
            df_q = df_q[["datetime", "data", "corrected_data", "discharge", "observation_stage", "q_observation", "offset", "q_offset", "precent_q_change", "RatingNumber", "estimate"]]
    return df_q