meta_cols = [
    "submitdate",
    "startdate",
    "datestamp",
    "tasks",
    "age",
    "gender_mf",
    "education",
    "UUID",
]

norm_bounds = {
    "Perceived Usefulness": (1, 7),
    "Perceived Ease of Use": (1, 7),
    "Self-Efficacy": (1, 10),
    "Mental Load": (0, 20),
    "Performance": (0, 20),
    "Effort": (0, 20),
    "Frustration": (0, 20)
}

type_dict = {
    "id": "Int64",
    "submitdate": "str",
    "lastpage": "string",
    "startlanguage": "string",
    "seed": "string",
    "token": "string",
    "startdate": "str",
    "datestamp": "str",
    "refurl": "string",
    "group": "string",
    "tasks": "Int64",
    "UUID": "string",
    "age": "string",
    "gender_mf": "string",
    "gender_other": "string",
    "education": "string",
    "usefulness[SQ001]": "Int64",
    "usefulness[SQ002]": "Int64",
    "usefulness[SQ003]": "Int64",
    "usefulness[SQ004]": "Int64",
    "usefulness[SQ005]": "Int64",
    "usefulness[SQ006]": "Int64",
    "ease_of_use[SQ001]": "Int64",
    "ease_of_use[SQ002]": "Int64",
    "ease_of_use[SQ003]": "Int64",
    "ease_of_use[SQ004]": "Int64",
    "ease_of_use[SQ005]": "Int64",
    "ease_of_use[SQ006]": "Int64",
    "self_efficacy[SQ001]": "Int64",
    "self_efficacy[SQ002]": "Int64",
    "self_efficacy[SQ003]": "Int64",
    "self_efficacy[SQ004]": "Int64",
    "self_efficacy[SQ005]": "Int64",
    "self_efficacy[SQ006]": "Int64",
    "self_efficacy[SQ007]": "Int64",
    "self_efficacy[SQ008]": "Int64",
    "self_efficacy[SQ009]": "Int64",
    "self_efficacy[SQ010]": "Int64",
    "load[SQ001]": "Int64",
    "load[SQ002]": "Int64",
    "load[SQ003]": "Int64",
    "load[SQ004]": "Int64",
    "load[SQ005]": "Int64",
    "load[SQ006]": "Int64",
}

## create lists of columns for each construct
pu_cols = [col for col in type_dict.keys() if col.startswith("usefulness")]
peou_cols = [col for col in type_dict.keys() if col.startswith("ease_of_use")]
se_cols = [col for col in type_dict.keys() if col.startswith("self_efficacy")]
load_cols = [col for col in type_dict.keys() if col.startswith("load")]
