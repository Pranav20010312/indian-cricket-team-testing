import os, pandas as pd, numpy as np
from datetime import date

cwd = os.path.dirname(os.path.abspath(__file__))
inp = os.path.join(cwd, "Data HW1.xlsx")
out = os.path.join(cwd, "HW1_Solution.xlsx")

TODAY = date(2026, 2, 13)
INCOME_MAP = {1: 175, 2: 697.5, 3: 1397.5, 4: 2100, 5: 2787.5, 6: 4000}

demo = pd.read_excel(inp, sheet_name="Demographics")
scores = pd.read_excel(inp, sheet_name="Scores")

print("=" * 60)
print("Demographics:", demo.shape[0], "rows, Scores:", scores.shape[0], "rows")
print("=" * 60)

# Q1 & Q2
demo_clean = demo.copy()
print("Q1&Q2: Demographics_Clean -", demo_clean.shape[0], "rows")

# Q3: Filter problematic rows
print("
--- Q3: Filtered Rows ---")
reasons = []

def flag(mask, reason):
    for idx in demo.index[mask]:
        reasons.append((idx, reason))

m1 = demo["DOB"] == 0
flag(m1, "DOB is 0 (missing)")
print("  DOB=0:", m1.sum())

m2 = ~demo["INCOME LEVEL"].between(1, 6)
flag(m2, "INCOME LEVEL outside 1-6 range")
print("  INCOME LEVEL outside 1-6:", m2.sum())

m3 = (demo["HOW MANY WORK IN YOUR FAMILY"] == 0) & (demo["INCOME LEVEL"] > 1)
flag(m3, "No workers but INCOME LEVEL > 1")
print("  No workers but income>1:", m3.sum())

m4 = (demo["HOW MANY WORK IN YOUR FAMILY"] > demo["FAMILY SIZE"]) & (demo["FAMILY SIZE"] > 0)
flag(m4, "Workers > Family Size")
print("  Workers > Family Size:", m4.sum())

m4b = (demo["HOW MANY WORK IN YOUR FAMILY"] > 0) & (demo["FAMILY SIZE"] == 0)
flag(m4b, "Workers > 0 but Family Size = 0")
print("  Workers>0 but FamilySize=0:", m4b.sum())

m5 = demo["FAMILY SIZE"] < 0
flag(m5, "Negative FAMILY SIZE")
m6 = demo["HOW MANY WORK IN YOUR FAMILY"] < 0
flag(m6, "Negative HOW MANY WORK")
print("  Negative Family Size:", m5.sum(), "Negative Workers:", m6.sum())

m7 = ~demo["LEVEL EDUCATION FATHER"].between(0, 10)
flag(m7, "Father Education outside 0-10")
m8 = ~demo["LEVEL EDUCATION MOTHER"].between(0, 10)
flag(m8, "Mother Education outside 0-10")
print("  Father edu out of range:", m7.sum(), "Mother edu out of range:", m8.sum())

reason_df = pd.DataFrame(reasons, columns=["idx", "FILTER_REASON"])
flagged_indices = reason_df["idx"].unique()
rg = reason_df.groupby("idx")["FILTER_REASON"].apply(lambda x: "; ".join(x)).reset_index()
rg.columns = ["idx", "FILTER_REASON"]

q3_filtered = demo.loc[flagged_indices].copy()
q3_filtered = q3_filtered.merge(rg, left_index=True, right_on="idx", how="left")
q3_filtered = q3_filtered.drop(columns=["idx"]).reset_index(drop=True)
print("  Total unique flagged rows:", len(flagged_indices))

summary_data = reason_df["FILTER_REASON"].value_counts().reset_index()
summary_data.columns = ["Filter Rule", "Count"]
for _, r in summary_data.iterrows():
    print("   ", r["Filter Rule"], ":", r["Count"])

# Q4: Age from DOB
print("
--- Q4: Age Computation ---")

def parse_dob_and_age(dob_int):
    if dob_int == 0:
        return np.nan
    s = str(int(dob_int))
    if len(s) == 7:
        day, month, year = int(s[0]), int(s[1:3]), int(s[3:7])
    elif len(s) == 8:
        day, month, year = int(s[0:2]), int(s[2:4]), int(s[4:8])
    else:
        return np.nan
    if month < 1 or month > 12 or day < 1 or day > 31 or year < 1900 or year > 2010:
        return np.nan
    try:
        birth = date(year, month, day)
        return int((TODAY - birth).days / 365.25)
    except Exception:
        return np.nan

demo_age = demo.copy()
demo_age["AGE"] = demo_age["DOB"].apply(parse_dob_and_age)
va = demo_age["AGE"].dropna()
print("  Valid ages:", len(va), "/", len(demo_age))
print("  Age range:", int(va.min()), "-", int(va.max()))
print("  Mean age: %.1f, Median age: %.1f" % (va.mean(), va.median()))

# Q5: Income per family member
print("
--- Q5: Income per Family Member ---")
demo_income = demo.copy()
demo_income["INCOME_MIDPOINT"] = demo_income["INCOME LEVEL"].map(INCOME_MAP)
demo_income["EFFECTIVE_FAMILY_SIZE"] = demo_income["FAMILY SIZE"].replace(0, 1)
demo_income["INCOME_PER_MEMBER"] = demo_income["INCOME_MIDPOINT"] / demo_income["EFFECTIVE_FAMILY_SIZE"]

valid_mask = demo_income["INCOME LEVEL"].between(1, 6)
median_ipm = demo_income.loc[valid_mask, "INCOME_PER_MEMBER"].median()
print("  Valid rows:", valid_mask.sum())
print("  MEDIAN monthly income per family member: %.2f" % median_ipm)

# Q6: 2D Pivot
print("
--- Q6: Pivot Income by Father x Mother Education ---")
q6_data = demo_income[valid_mask].copy()
q6_pivot = q6_data.pivot_table(
    values="INCOME_PER_MEMBER",
    index="LEVEL EDUCATION FATHER",
    columns="LEVEL EDUCATION MOTHER",
    aggfunc="median"
)
print("  Pivot shape:", q6_pivot.shape)
print(q6_pivot.round(1).to_string())

# Q7: Family Size vs NEM
print("
--- Q7: Family Size vs NEM ---")
merged = scores.merge(demo[["MRUN", "FAMILY SIZE"]], on="MRUN", how="inner")
q7_pivot = merged.groupby("FAMILY SIZE")["NEM"].mean().reset_index()
q7_pivot.columns = ["FAMILY_SIZE", "AVG_NEM"]
print(q7_pivot.round(1).to_string(index=False))

# Q8: Avg (MATE+LYC)/2 by parent education
print("
--- Q8: Avg (MATE+LYC)/2 by Parent Education ---")
merged_full = scores.merge(demo[["MRUN", "LEVEL EDUCATION FATHER", "LEVEL EDUCATION MOTHER"]], on="MRUN", how="inner")
merged_full["AVG_SCORE"] = (merged_full["MATE"] + merged_full["LYC"]) / 2

q8_mother = merged_full.groupby("LEVEL EDUCATION MOTHER")["AVG_SCORE"].mean().reset_index()
q8_mother.columns = ["LEVEL_EDUCATION_MOTHER", "AVG_SCORE"]
print("  By Mother Education:")
print(q8_mother.round(1).to_string(index=False))

q8_father = merged_full.groupby("LEVEL EDUCATION FATHER")["AVG_SCORE"].mean().reset_index()
q8_father.columns = ["LEVEL_EDUCATION_FATHER", "AVG_SCORE"]
print("  By Father Education:")
print(q8_father.round(1).to_string(index=False))

mother_range = q8_mother["AVG_SCORE"].max() - q8_mother["AVG_SCORE"].min()
father_range = q8_father["AVG_SCORE"].max() - q8_father["AVG_SCORE"].min()
print("  Mother edu score range: %.1f" % mother_range)
print("  Father edu score range: %.1f" % father_range)
bigger = "Father" if father_range > mother_range else "Mother"
print("  ->", bigger, "education has bigger effect")

# Q9: Income Level vs Test Scores
print("
--- Q9: Income Level vs Test Scores ---")
merged_inc = scores.merge(demo[["MRUN", "INCOME LEVEL"]], on="MRUN", how="inner")
score_cols = ["NEM", "LYC", "MATE", "HYCS", "CIEN"]
q9_pivot = merged_inc.groupby("INCOME LEVEL")[score_cols].mean().reset_index()
print(q9_pivot.round(1).to_string(index=False))

# Q10: HST vs Income Level
print("
--- Q10: High School Type vs Income Level ---")
merged_hst = scores.merge(demo[["MRUN", "INCOME LEVEL"]], on="MRUN", how="inner")
q10_counts = pd.crosstab(merged_hst["HST"], merged_hst["INCOME LEVEL"], margins=True)
print("  Counts:")
print(q10_counts.to_string())

q10_pct = pd.crosstab(merged_hst["HST"], merged_hst["INCOME LEVEL"], normalize="index").multiply(100).round(1)
print("  Row Percentages:")
print(q10_pct.to_string())

# WRITE OUTPUT EXCEL
print("
" + "=" * 60)
print("Writing output file...")

with pd.ExcelWriter(out, engine="openpyxl") as writer:
    demo_clean.to_excel(writer, sheet_name="Demographics_Clean", index=False)
    
    q3_filtered.to_excel(writer, sheet_name="Q3_Filtered", index=False)
    sr = len(q3_filtered) + 3
    summary_data.to_excel(writer, sheet_name="Q3_Filtered", startrow=sr, index=False)
    
    demo_age.to_excel(writer, sheet_name="Q4_Age", index=False)
    
    q5_out = demo_income[["MRUN", "DOB", "FAMILY SIZE", "HOW MANY WORK IN YOUR FAMILY",
                           "INCOME LEVEL", "LEVEL EDUCATION FATHER", "LEVEL EDUCATION MOTHER",
                           "INCOME_MIDPOINT", "EFFECTIVE_FAMILY_SIZE", "INCOME_PER_MEMBER"]].copy()
    q5_out.to_excel(writer, sheet_name="Q5_Income_PerMember", index=False)
    mr = pd.DataFrame({"Metric": ["MEDIAN Income Per Family Member"], "Value": [median_ipm]})
    mr.to_excel(writer, sheet_name="Q5_Income_PerMember", startrow=len(q5_out)+3, index=False)
    
    q6_pivot.to_excel(writer, sheet_name="Q6_Pivot_Income_Education")
    
    q7_pivot.to_excel(writer, sheet_name="Q7_Pivot_FamilySize_NEM", index=False)
    
    q8_mother.to_excel(writer, sheet_name="Q8_Pivot_Mother_Scores", index=False)
    q8_father.to_excel(writer, sheet_name="Q8_Pivot_Father_Scores", index=False)
    nt = bigger + " education shows larger variation (" + "%.1f" % max(mother_range,father_range) + " vs " + "%.1f" % min(mother_range,father_range) + " point range)"
    note = pd.DataFrame({"Note": [nt]})
    note.to_excel(writer, sheet_name="Q8_Pivot_Mother_Scores", startrow=len(q8_mother)+3, index=False)
    note.to_excel(writer, sheet_name="Q8_Pivot_Father_Scores", startrow=len(q8_father)+3, index=False)
    
    q9_pivot.to_excel(writer, sheet_name="Q9_Pivot_Income_Scores", index=False)
    
    q10_counts.to_excel(writer, sheet_name="Q10_Pivot_HST_Income")
    pr = len(q10_counts) + 3
    lbl = pd.DataFrame({"Label": ["Row Percentages (%)"]})
    lbl.to_excel(writer, sheet_name="Q10_Pivot_HST_Income", startrow=pr, index=False)
    q10_pct.to_excel(writer, sheet_name="Q10_Pivot_HST_Income", startrow=pr+2)

print("OUTPUT FILE WRITTEN SUCCESSFULLY!")
print("Output:", out)
print("=" * 60)
