
from datetime import datetime
from typing import Optional



from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper


class SaveInput(BaseModel):
    data: str = Field(..., description="Structured fitness plan text to save.")
    filename: Optional[str] = Field(default="fitness_plan.txt")

def save_to_txt(data: str, filename: str = "fitness_plan.txt") -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Fitness Plan ---\nTimestamp: {timestamp}\n\n{data}\n\n"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)
    return f"Saved to {filename}"
save_tool = StructuredTool.from_function(
    name="save_text_to_file",
    description="Save the final structured fitness plan to a file.",
    func=save_to_txt,
    args_schema=SaveInput,
)


_ddg = DuckDuckGoSearchRun()

class SearchInput(BaseModel):
    query: str = Field(..., description="Search query (fitness/nutrition).")

def _search(query: str) -> str:
    return _ddg.run(query)

search_tool = StructuredTool.from_function(
    name="search",
    description="Search the web (DuckDuckGo) for fitness/nutrition references.",
    func=_search,
    args_schema=SearchInput,
)


_api = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1500)
_wiki = WikipediaQueryRun(api_wrapper=_api)

class WikiInput(BaseModel):
    query: str

def _wiki(query: str) -> str:
    return _wiki.run(query)

wiki_tool = StructuredTool.from_function(
    name="wikipedia",
    description="Look up concise background/definitions on Wikipedia (e.g., VO2max).",
    func=_wiki,
    args_schema=WikiInput,
)


class BMIInput(BaseModel):
    weight: float = Field(..., description="Weight (kg)")
    height: float = Field(..., description="Height (cm)")

def _bmi(weight: float, height: float) -> str:
    m = height / 100
    bmi = weight / (m * m)
    cat = (
        "Underweight" if bmi < 18.5
        else "Normal weight" if bmi < 25
        else "Overweight" if bmi < 30
        else "Obesity"
    )
    return f"{bmi:.1f} ({cat})"

bmi_tool = StructuredTool.from_function(
    name="bmi_tool",
    description="Calculate BMI and category.",
    func=_bmi,
    args_schema=BMIInput,
)


class TDEEInput(BaseModel):
    sex: str = Field(..., description="'male' or 'female'")
    age: float = Field(..., description="Age in years.")
    height: float = Field(..., description="Height in centimeters.")
    weight: float = Field(..., description="Weight in kilograms.")
    activity_level: str = Field(
        ...,
        description="Accepts many variants: sedentary, lightly active, light exercise, moderate/moderately active, active, very active, extra active, etc."
    )

def _normalize_activity(s: str) -> str:
    s = (s or "").lower().strip()
    pairs = [
        ({"sedentary", "none", "no exercise", "inactive", "desk job"}, "sedentary"),
        ({"light", "lightly active", "light exercise", "light exercise 1-2", "1-2x", "1-2 times/week"}, "light"),
        ({"moderate", "moderately active", "moderate exercise", "3-5x", "3-5 times/week"}, "moderate"),
        ({"active", "very active", "6-7x", "6-7 times/week", "physical job"}, "active"),
        ({"extra active", "athlete", "two-a-day", "twice daily"}, "very_active"),
    ]
    for keys, canon in pairs:
        if any(k in s for k in keys):
            return canon
    # fallback exact matches
    if s in {"sedentary", "light", "moderate", "active", "very_active"}:
        return s
    # last resort heuristic
    if "moderate" in s:
        return "moderate"
    if "light" in s:
        return "light"
    if "very" in s:
        return "very_active"
    if "active" in s:
        return "active"
    return "sedentary"

def _tdee(sex: str, age: float, height: float, weight: float, activity_level: str) -> str:
    sex = sex.lower().strip()
    if sex not in {"male", "female"}:
        raise ValueError("sex must be 'male' or 'female'")

    # Mifflin–St Jeor BMR
    if sex == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    canon = _normalize_activity(activity_level)
    mults = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    tdee = bmr * mults[canon]
    return f"{tdee:.0f}"

tdee_tool = StructuredTool.from_function(
    name="tdee_tool",
    description="Estimate total daily energy expenditure with Mifflin–St Jeor and robust activity normalization.",
    func=_tdee,
    args_schema=TDEEInput,
)


class MacroInput(BaseModel):
    calories: int = Field(..., description="Daily calories.")
    weight: float = Field(..., description="Weight in kg (for protein target).")
    goal: str = Field(..., description="fat_loss | maintenance | muscle_gain (synonyms accepted)")

def _normalize_goal(g: str) -> str:
    g = (g or "").lower().strip()
    if any(k in g for k in ["loss", "cut", "deficit", "fat"]):
        return "fat_loss"
    if any(k in g for k in ["gain", "bulk", "surplus", "muscle"]):
        return "muscle_gain"
    return "maintenance"

def _macros(calories: int, weight: float, goal: str) -> str:
    g = _normalize_goal(goal)
    protein_g = 2.0 * weight  # 
    protein_kcal = protein_g * 4
    fat_pct = 0.25 if g == "fat_loss" else 0.30 if g == "muscle_gain" else 0.27
    fat_kcal = calories * fat_pct
    fat_g = fat_kcal / 9
    remaining = max(0, calories - (protein_kcal + fat_kcal))
    carb_g = remaining / 4
    return (
        f"goal={g}, protein_g={protein_g:.0f}, fat_g={fat_g:.0f}, carbs_g={carb_g:.0f}, "
        f"protein_kcal={protein_kcal:.0f}, fat_kcal={fat_kcal:.0f}, carb_kcal={remaining:.0f}"
    )

macros_tool = StructuredTool.from_function(
    name="macros_tool",
    description="Compute protein/fat/carb grams from calories, weight (kg), and goal (accepts synonyms).",
    func=_macros,
    args_schema=MacroInput,
)


class ConvertInput(BaseModel):
    
    
    value: float
    from_unit: str
    to_unit: str

def _convert(value: float, from_unit: str, to_unit: str) -> str:
    u = (from_unit.lower().strip(), to_unit.lower().strip())
    if u == ("kg", "lb"): return f"{value * 2.20462:.2f}"
    if u == ("lb", "kg"): return f"{value / 2.20462:.2f}"
    if u == ("cm", "in"): return f"{value / 2.54:.2f}"
    if u == ("in", "cm"): return f"{value * 2.54:.2f}"
    if from_unit.lower() == to_unit.lower(): return f"{value:.2f}"
    raise ValueError("Unsupported conversion. Use kg|lb|cm|in")

unit_convert_tool = StructuredTool.from_function(
    name="unit_convert_tool",
    description="Convert between kg↔lb and cm↔in.",
    func=_convert,
    args_schema=ConvertInput,
)
