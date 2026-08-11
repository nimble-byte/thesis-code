import pandas as pd

v0 = pd.read_csv("./codebooks/codebook_v0.csv").set_index("id")
v1 = pd.read_csv("./codebooks/codebook_v1.csv").set_index("id")
v2 = pd.read_csv("./codebooks/codebook_v2.csv").set_index("id")
v3 = pd.read_csv("./codebooks/codebook_v3.csv").set_index("id")


def compare_cols(source: pd.DataFrame, compare: pd.DataFrame, col: list):
    """
    Compare columns of two dataframes and return a dataframe with the differences.

    Args:
        source (pd.DataFrame): The source dataframe.
        compare (pd.DataFrame): The dataframe to compare against.
        col (list): List of columns to compare.
    """
    diff = pd.DataFrame(columns=col)
    for c in col:
        diff[c] = source[c] != compare[c]
    return diff


def assert_no_diff(diff: pd.DataFrame):
    """
    Assert that there are no differences in the dataframe.

    Args:
        diff (pd.DataFrame): The dataframe with differences.
    """
    assert not diff.any().any(), f"Differences found:\n{diff[diff.any(axis=1)]}"

v0_v1 = compare_cols(v0, v1, ["raw_code"])
v1_v2 = compare_cols(v1, v2, ["raw_code", "canonical_code"])
v2_v3 = compare_cols(v2, v3, ["raw_code", "canonical_code", "pattern_code"])

assert_no_diff(v0_v1)
assert_no_diff(v1_v2)
assert_no_diff(v2_v3)

print("All codebooks are consistent across versions.")
