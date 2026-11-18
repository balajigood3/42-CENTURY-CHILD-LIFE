import json
from datetime import date
import streamlit as st
from .planner import create_plan, progress_summary

st.set_page_config(page_title="AI Goal Achievement Agent", page_icon="🎯", layout="wide")
st.title("AI Goal Achievement Agent")
st.caption("Goal → milestones → dependent tasks → progress tracking")
st.warning("This tool creates a plan and tracks manual progress. It does not perform tasks or guarantee goal completion.")

with st.form("goal_form"):
    goal = st.text_area("Your goal", placeholder="Example: Build and publish a portfolio website with three AI projects.", height=110)
    deadline = st.number_input("Deadline (days)", min_value=1, max_value=3650, value=30)
    use_ollama = st.checkbox("Use local Ollama model when available", value=True)
    submitted = st.form_submit_button("Create goal plan", type="primary")

if submitted:
    try:
        plan, status = create_plan(goal, int(deadline), use_ollama)
        st.session_state["plan"] = plan.model_dump()
        st.session_state["plan_status"] = status
        st.session_state["completed_ids"] = []
    except Exception as exc:
        st.error(str(exc))

if "plan" in st.session_state:
    from .models import GoalPlan
    plan = GoalPlan.model_validate(st.session_state["plan"])
    st.success(st.session_state["plan_status"])
    st.subheader(plan.goal)
    st.write(f"Planning deadline: **{plan.deadline_days} days**")
    st.markdown("**Milestones**")
    for i, milestone in enumerate(plan.milestones, 1):
        st.write(f"{i}. {milestone}")
    st.markdown("**Assumptions**")
    for assumption in plan.assumptions:
        st.write(f"- {assumption}")

    completed = set(st.session_state.get("completed_ids", []))
    st.subheader("Progress tracker")
    progress = progress_summary(plan, completed)
    st.progress(progress["percent"] / 100, text=f'{progress["percent"]}% complete · {progress["completed"]}/{progress["total"]} tasks')
    with st.form("progress_form"):
        updated = []
        for task in plan.ordered_tasks():
            checked = st.checkbox(
                f'{task.id} · {task.title} ({task.priority}, {task.estimated_days} day(s))',
                value=task.id in completed,
                key=f"done_{task.id}"
            )
            if checked:
                updated.append(task.id)
        save_progress = st.form_submit_button("Save progress")
    if save_progress:
        st.session_state["completed_ids"] = updated
        st.rerun()

    progress = progress_summary(plan, set(st.session_state.get("completed_ids", [])))
    col1, col2, col3 = st.columns(3)
    col1.metric("Completed", progress["completed"])
    col2.metric("Ready to start", len(progress["ready"]))
    col3.metric("Blocked by dependencies", len(progress["blocked"]))
    st.write("**Ready tasks:** " + (", ".join(progress["ready"]) or "None"))
    st.write("**Blocked tasks:** " + (", ".join(progress["blocked"]) or "None"))

    st.subheader("Task details")
    for task in plan.ordered_tasks():
        with st.expander(f"{task.id} · {task.title}"):
            st.write(task.description)
            st.write(f"**Milestone:** {task.milestone}")
            st.write(f"**Dependencies:** {', '.join(task.depends_on) or 'None'}")
            st.write(f"**Success criteria:** {task.success_criteria}")
    payload = json.dumps({"plan":plan.model_dump(),"completed_task_ids":sorted(st.session_state.get("completed_ids",[]))}, indent=2, ensure_ascii=False)
    st.download_button("Download plan and progress JSON", payload, "goal_plan_progress.json", "application/json")
