from config import MAX_INPUT_CHARS
from core.llm import ask_json
from core.prompts import COMPARE_PROMPT
ALLOWED={"CONTRADICTION","CONSISTENT","DIFFERENT_SCOPE","UNCLEAR"}
def detect_contradictions(source_a,source_b,objective=""):
    ta=source_a.get("text","").strip(); tb=source_b.get("text","").strip()
    if not ta or not tb: raise ValueError("இரண்டு ஆதாரங்களிலும் உரை கட்டாயம்.")
    if len(ta)>MAX_INPUT_CHARS or len(tb)>MAX_INPUT_CHARS: raise ValueError(f"ஒவ்வொரு உரையும் {MAX_INPUT_CHARS} characters-க்குள் இருக்க வேண்டும்.")
    data=ask_json(COMPARE_PROMPT.format(name_a=source_a.get("name","Source A"),name_b=source_b.get("name","Source B"),text_a=ta,text_b=tb,objective=objective or "Identify material factual conflicts."))
    comparisons=[]
    for item in data.get("comparisons",[]) if isinstance(data.get("comparisons",[]),list) else []:
        if not isinstance(item,dict): continue
        status=str(item.get("status","UNCLEAR")).upper()
        if status not in ALLOWED: status="UNCLEAR"
        comparisons.append({"topic":str(item.get("topic","Unspecified topic")),"source_a_claim":str(item.get("source_a_claim","")),"source_b_claim":str(item.get("source_b_claim","")),"status":status,"explanation":str(item.get("explanation","")),"resolution":str(item.get("resolution","மூல ஆவணத்தைச் சரிபார்க்கவும்."))})
    overall="CONTRADICTIONS_FOUND" if any(x["status"]=="CONTRADICTION" for x in comparisons) else ("UNCLEAR" if not comparisons or any(x["status"]=="UNCLEAR" for x in comparisons) else "NO_DIRECT_CONTRADICTION_FOUND")
    return {"overall_status":overall,"summary":str(data.get("summary","சுருக்கம் கிடைக்கவில்லை.")),"comparisons":comparisons}
