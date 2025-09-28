
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any



from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import (
    search_tool,
    wiki_tool,
    save_tool,
    bmi_tool,
    tdee_tool,
    macros_tool,
    unit_convert_tool,
)

load_dotenv()  



class FitnessResponse(BaseModel):
    user_profile: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parsed user info and assumptions. Include keys like age, sex, height_cm, weight_kg, activity_level, equipment, injuries, assumptions, missing_fields.",
    )
    goal: str = Field(..., description="Primary goal (e.g., fat loss, muscle gain, endurance).")
    training_plan: List[Dict[str, Any]] = Field(
        ...,
        description="Day-by-day plan; each item can include day, focus, exercises (with sets x reps x RPE/%1RM), warmup, progressions."
    )
    cardio_plan: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Cardio recommendations (type, intensity, duration, frequency)."
    )
    nutrition: Dict[str, Any] = Field(
        ...,
        description="Calories, macros (g), sample day, hydration."
    )
    recovery: Dict[str, Any] = Field(
        ...,
        description="Sleep, deload/mobility/rest guidance."
    )
    metrics_to_track: List[str] = Field(
        default_factory=lambda: ["weight (weekly avg)", "waist", "progress photos", "reps @ RPE", "sleep hours"]
    )
    cautions: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)



llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_version="v1",
    transport="rest",
)

parser = PydanticOutputParser(pydantic_object=FitnessResponse)






prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are FitGuidePro, a certified fitness & nutrition assistant.

HARD RULES:
- Return ONLY a JSON object that matches the FitnessResponse schema provided in {format_instructions}.
- DO NOT ask follow-up questions in the output. If any information is missing, MAKE REASONABLE ASSUMPTIONS and list them under user_profile.assumptions, and list what was missing under user_profile.missing_fields.
- Use tools when helpful:
  - bmi_tool, tdee_tool, macros_tool for numbers
  - unit_convert_tool for units
  - search, wikipedia for citations
  - save_text_to_file ONLY after you produce the final JSON (optional)
- Safety first.

No extra words outside JSON.
{format_instructions}
""",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())


tools = [
    search_tool,
    wiki_tool,
    save_tool,
    bmi_tool,
    tdee_tool,
    macros_tool,
    unit_convert_tool,
]


agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,   
)


if __name__ == "__main__":
    query = input("Tell me your goal (e.g., 'Lose fat, 23yo male, 5'9, 80kg, desk job, dumbbells at home'): ")
    raw = agent_executor.invoke({"query": query, "chat_history": []})

    output_text = raw.get("output") if isinstance(raw, dict) else str(raw)

    try:
        structured = parser.parse(output_text)

        # Raw JSON
        print("\n=== RAW JSON OUTPUT ===")
        print(structured.model_dump_json(indent=2))

        # Form View
        print("\n=== FITNESS PLAN (FORM VIEW) ===")
        print("👤 User Profile:")
        for k, v in structured.user_profile.items():
            print(f"   {k}: {v}")

        print(f"\n1. Goal:\n   {structured.goal}")

        print("\n2. Training Plan:")
        for i, day in enumerate(structured.training_plan, start=1):
            print(f"   {i}. {day.get('day','Unknown')}: {day.get('focus','')}")
            for ex in day.get("exercises", []):
                print(f"       • {ex}")

        if structured.cardio_plan:
            print("\n3. Cardio Plan:")
            for c in structured.cardio_plan:
                print(f"   - {c}")

        print("\n4. Nutrition:")
        for k, v in structured.nutrition.items():
            print(f"   {k}: {v}")

        print("\n5. Recovery:")
        for k, v in structured.recovery.items():
            print(f"   {k}: {v}")

        print("\n6. Metrics to Track:")
        for m in structured.metrics_to_track:
            print(f"   - {m}")

        print("\n7. Cautions:")
        for c in structured.cautions:
            print(f"   - {c}")

        print("\n8. Sources:")
        for s in structured.sources:
            print(f"   - {s}")

        print("\n9. Tools Used:")
        for t in structured.tools_used:
            print(f"   - {t}")

    except Exception as e:
        print("\n[WARN] Could not parse model output into FitnessResponse.")
        print("Error:", e)
        print("Raw output:\n", output_text)
