# ============================================================
# MINDMATE: AI-Powered Mental Health Companion for Students
# UNIFIED SINGLE-FILE PRODUCTION EDITION
# ============================================================

import array
import base64
import calendar
import json
import math
import os
import re
from datetime import datetime
from html import escape
from pathlib import Path
import random
import textwrap
import time
import wave
import zlib

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False


# ============================================================
# 1. PROJECT PATHS & DIRECTORY CREATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

DATA_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

DATABASE = DATA_DIR / "MindMate_Database.xlsx"
AUDIO_FILE = ASSETS_DIR / "soothing.mp3"
CIRCLE_DATA_FILE = DATA_DIR / "mindmate_circle.json"


# ============================================================
# 2. STREAMLIT PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MindMate 🌿 AI Mental Health Companion",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ------------------------------------------------------------
# 2b. DRAG-TO-SELECT WORD SEARCH COMPONENT (written to assets/)
# ------------------------------------------------------------

WORDSEARCH_HTML = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
html,body{margin:0;padding:0;background:transparent;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;overflow:hidden;}
#wrap{width:100%;display:flex;justify-content:center;padding:4px 0 8px 0;box-sizing:border-box;}
#board{position:relative;padding:12px;border-radius:26px;touch-action:none;user-select:none;-webkit-user-select:none;box-shadow:0 6px 22px rgba(0,0,0,.07);}
#svg{position:absolute;left:12px;top:12px;pointer-events:none;}
#grid{position:relative;display:grid;touch-action:none;cursor:pointer;}
.cell{display:flex;align-items:center;justify-content:center;font-weight:700;pointer-events:none;}
</style></head><body>
<div id="wrap"><div id="board"><svg id="svg"></svg><div id="grid"></div></div></div>
<script>
(function(){
var PAL=["#8CCFA9","#F3B6A3","#A9C8F0","#F2D58C","#C9B6EA","#9FDCD0","#F0A9C4","#BFD98A"];
var args=null,n=0,cell=40,drag=null,end=null;
function post(type,data){var m={isStreamlitMessage:true,type:type};for(var k in data){m[k]=data[k];}window.parent.postMessage(m,"*");}
function el(id){return document.getElementById(id);}
function ctr(r,c){return [c*cell+cell/2,r*cell+cell/2];}
function lineEl(r1,c1,r2,c2,color,op){
  var a=ctr(r1,c1),b=ctr(r2,c2);
  return '<line x1="'+a[0]+'" y1="'+a[1]+'" x2="'+b[0]+'" y2="'+b[1]+'" stroke="'+color+'" stroke-opacity="'+op+'" stroke-width="'+(cell*0.78)+'" stroke-linecap="round"/>';
}
function drawLines(){
  if(!args)return;
  var s="",segs=args.segments||[];
  for(var i=0;i<segs.length;i++){var q=segs[i];s+=lineEl(q.r1,q.c1,q.r2,q.c2,PAL[i%PAL.length],0.75);}
  if(drag&&end){s+=lineEl(drag.r,drag.c,end.r,end.c,args.dark?"#8EAFA0":"#6E8B74",0.45);}
  el("svg").innerHTML=s;
}
function render(){
  if(!args)return;
  var g=args.grid||[];n=g.length;
  var dark=!!args.dark;
  var wrapW=el("wrap").clientWidth||340;
  cell=Math.max(26,Math.min(46,Math.floor((wrapW-40)/n)));
  var board=el("board");
  board.style.background=dark?"#1A2320":"#FFFFFF";
  board.style.border="1px solid "+(dark?"#2D3A34":"#EAE5DE");
  var grid=el("grid");
  grid.style.gridTemplateColumns="repeat("+n+","+cell+"px)";
  grid.style.gridAutoRows=cell+"px";
  grid.style.color=dark?"#ECEFED":"#2C3531";
  grid.innerHTML="";
  for(var r=0;r<n;r++){for(var c=0;c<n;c++){
    var d=document.createElement("div");d.className="cell";
    d.style.fontSize=Math.round(cell*0.46)+"px";d.textContent=g[r].charAt(c);grid.appendChild(d);
  }}
  var svg=el("svg");svg.setAttribute("width",n*cell);svg.setAttribute("height",n*cell);
  drawLines();
  post("streamlit:setFrameHeight",{height:n*cell+24+16});
}
function cellAt(e){
  var rect=el("grid").getBoundingClientRect();
  return {r:Math.floor((e.clientY-rect.top)/cell),c:Math.floor((e.clientX-rect.left)/cell)};
}
function inside(p){return p.r>=0&&p.r<n&&p.c>=0&&p.c<n;}
function snap(p){
  var dr=p.r-drag.r,dc=p.c-drag.c;
  if(dr===0&&dc===0)return {r:drag.r,c:drag.c};
  var step=Math.round(Math.atan2(dr,dc)/(Math.PI/4));
  var ux=Math.round(Math.cos(step*Math.PI/4)),uy=Math.round(Math.sin(step*Math.PI/4));
  var len=Math.max(Math.abs(dr),Math.abs(dc));
  while(len>0){
    var rr=drag.r+uy*len,cc=drag.c+ux*len;
    if(rr>=0&&rr<n&&cc>=0&&cc<n)return {r:rr,c:cc};
    len--;
  }
  return {r:drag.r,c:drag.c};
}
function finish(){
  if(!drag||!end){drag=null;end=null;drawLines();return;}
  var dr=Math.sign(end.r-drag.r),dc=Math.sign(end.c-drag.c);
  var len=Math.max(Math.abs(end.r-drag.r),Math.abs(end.c-drag.c))+1;
  var w="";
  for(var i=0;i<len;i++){w+=args.grid[drag.r+dr*i].charAt(drag.c+dc*i);}
  var rev=w.split("").reverse().join("");
  var words=args.words||[],found=args.found||[],hit=null;
  if(len>1){
    if(words.indexOf(w)>=0)hit=w;else if(words.indexOf(rev)>=0)hit=rev;
  }
  if(hit&&found.indexOf(hit)<0){
    var seg={word:hit,r1:drag.r,c1:drag.c,r2:end.r,c2:end.c};
    args.segments=(args.segments||[]).concat([seg]);
    post("streamlit:setComponentValue",{value:{word:hit,r1:seg.r1,c1:seg.c1,r2:seg.r2,c2:seg.c2,nonce:Date.now()+"_"+Math.random()},dataType:"json"});
  }
  drag=null;end=null;drawLines();
}
var grid=el("grid");
grid.addEventListener("pointerdown",function(e){
  var p=cellAt(e);if(!inside(p))return;
  e.preventDefault();drag=p;end=p;
  try{grid.setPointerCapture(e.pointerId);}catch(x){}
  drawLines();
});
grid.addEventListener("pointermove",function(e){
  if(!drag)return;e.preventDefault();end=snap(cellAt(e));drawLines();
});
grid.addEventListener("pointerup",function(){if(drag)finish();});
grid.addEventListener("pointercancel",function(){drag=null;end=null;drawLines();});
window.addEventListener("message",function(ev){
  var d=ev.data;
  if(d&&d.type==="streamlit:render"){args=d.args;render();}
});
window.addEventListener("resize",render);
post("streamlit:componentReady",{apiVersion:1});
})();
</script></body></html>
"""

COMPONENT_DIR = ASSETS_DIR / "mm_wordsearch"
try:
    COMPONENT_DIR.mkdir(parents=True, exist_ok=True)
    _component_file = COMPONENT_DIR / "index.html"
    if not _component_file.exists() or _component_file.read_text(encoding="utf-8") != WORDSEARCH_HTML:
        _component_file.write_text(WORDSEARCH_HTML, encoding="utf-8")
    mm_wordsearch = components.declare_component("mm_wordsearch", path=str(COMPONENT_DIR))
except Exception:
    mm_wordsearch = None



# ============================================================
# 3. GLOBAL SESSION STATE INITIALIZATION
# ============================================================

DEFAULT_STATE = {
    "page": "Home",
    "theme_mode": "light",
    "brain_dump_result": None,
    "brain_dump_plan": None,
    "plan_checkins": {},
    "messages": [],
    "mood": None,
    "mood_history": [],
    "pending_message": None,
    "temp_message_input": "",
    "active_timer_id": None,
    "timer_running": False,
    "timer_seconds_left": 0,
    "student_name": "",
    "student_id": None,
    "student_class": None,
    "user_registered": False,
    "trusted_adult_info": None,
    "selected_resource_id": None,
    "suppress_activities": False,

    # UI Toggles
    "explore_tab": "resources",
    "res_content_type": "articles",
    "dump_mode": "type",

    # Circle State
    "circle_selected_dm_post": None,

    # Mini-Games State
    "memory_cards": [],
    "memory_flipped": [],
    "memory_matched": [],
    "memory_moves": 0,
    "scramble_word": None,
    "scramble_jumbled": None,
    "scramble_score": 0,
    "pattern_seq": [],
    "pattern_answer": None,
    "pattern_score": 0,
    "emoji_seq": [],
    "emoji_options": [],
    "emoji_score": 0,
    "odd_items": [],
    "odd_answer": None,
    "odd_score": 0,
    "crossword_selected": [],
    "crossword_found_words": [],

    # Game levels / reshuffle state
    "memory_level": 1,
    "scramble_round": 0,
    "pattern_round": 0,
    "pattern_hint": "",
    "emoji_answer": None,
    "emoji_round": 0,
    "odd_round": 0,
    "crossword_level": 1,
    "crossword_grid": [],
    "crossword_words": [],
    "crossword_segments": [],
    "crossword_last_nonce": None,
    "crossword_round": 0,
    "game_feedback": {},

    # Circle feed state
    "circle_liked": set(),
    "circle_open_comments": set(),
    "circle_reply_to": None,

    # Brain Dump records (left sidebar)
    "dump_records": [],
    "dump_just_completed": None,
    "dump_reset_pending": False,
    "brain_dump_raw": "",

    # Chat intelligence, limits and app lock
    "chat_ctx": {
        "turns": 0, "topic_counts": {}, "last_topic": None, "distress_hits": 0,
        "last_support_turn": -99, "last_resource_turn": -99, "shown_resources": [],
        "awaiting": None, "last_light_turn": -99,
    },
    "severe_flag_ts": None,
    "chat_prev_page": None,
    "chat_session_start": None,
    "chat_last_msg_ts": None,
    "chat_reminder_shown": False,
    "app_locked": False,
    "last_activity": None,

    # Music
    "music_choice": None,
}

for key, default_value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


# ============================================================
# 4. DATABASE & TOP-LEVEL HELPER FUNCTIONS
# ============================================================

@st.cache_data
def get_sheet_names():
    if not DATABASE.exists():
        return []
    try:
        excel_file = pd.ExcelFile(DATABASE)
        return excel_file.sheet_names
    except Exception:
        return []


@st.cache_data
def load_sheet(sheet_name):
    if not DATABASE.exists():
        return pd.DataFrame()
    try:
        available_sheets = get_sheet_names()
        if sheet_name not in available_sheets:
            return pd.DataFrame()
        return pd.read_excel(DATABASE, sheet_name=sheet_name)
    except Exception:
        return pd.DataFrame()


responses_df = load_sheet("05_Responses")
activities_df = load_sheet("06_Activities")
games_df = load_sheet("07_Games")
resources_df = load_sheet("08_Resources")
trusted_adults_df = load_sheet("09_Trusted_Adults")


def append_to_excel(sheet_name, new_data_dict):
    if not DATABASE.exists():
        try:
            df = pd.DataFrame([new_data_dict])
            with pd.ExcelWriter(DATABASE, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            return
        except Exception:
            return
    try:
        with pd.ExcelWriter(
            DATABASE, mode="a", engine="openpyxl", if_sheet_exists="overlay"
        ) as writer:
            try:
                existing_df = pd.read_excel(DATABASE, sheet_name=sheet_name)
                updated_df = pd.concat(
                    [existing_df, pd.DataFrame([new_data_dict])], ignore_index=True
                )
            except Exception:
                updated_df = pd.DataFrame([new_data_dict])
            updated_df.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception:
        pass


def clean_value(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    value = str(value).strip()
    return None if value.lower() in {"", "nan", "none", "null"} else value


def safe_text(value, default=""):
    cleaned = clean_value(value)
    return default if cleaned is None else cleaned


def predict_intent(text):
    t = text.lower()
    if any(w in t for w in ["anxious", "panic", "scared", "worry", "stress", "stressed", "overwhelmed"]):
        return "anxiety"
    elif any(w in t for w in ["study", "exam", "test", "school", "assignment", "chapter", "homework"]):
        return "academic_stress"
    elif any(w in t for w in ["sad", "depressed", "down", "cry", "lonely", "low"]):
        return "low_mood"
    elif any(w in t for w in ["tired", "sleep", "exhausted", "burnout"]):
        return "fatigue"
    return "general_chat"


def load_circle_data():
    default = {
        "moods": [{"mood": "stressed", "date": datetime.now().strftime("%Y-%m-%d")}],
        "posts": [
            {
                "id": "P-101",
                "text": "Studied for 4 hours and still feel like I know nothing for physics... anyone else?",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "reactions": {"❤️ Same here": 8, "🫂 You're not alone": 12, "🔥 We got this": 5},
                "comments": [
                    {"id": "C-201", "text": "Same!! Try a 25 min focus + 5 min break cycle. It helped me a lot 🌿", "date": datetime.now().strftime("%Y-%m-%d"), "sid": "seed-a", "likes": 6,
                     "replies": [{"id": "R-301", "text": "Going to try this tonight, thank you!", "date": datetime.now().strftime("%Y-%m-%d"), "sid": "seed-b", "likes": 2}]},
                    {"id": "C-202", "text": "Feeling like you know nothing usually means you're learning. You've got this 💚", "date": datetime.now().strftime("%Y-%m-%d"), "sid": "seed-c", "likes": 9, "replies": []}
                ]
            },
            {
                "id": "P-102",
                "text": "Friendly reminder to grab a glass of water and stretch your neck right now! 🌿",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "reactions": {"❤️ Same here": 4, "🫂 You're not alone": 3, "🔥 We got this": 15},
                "comments": [
                    {"id": "C-203", "text": "Just drank water and stretched. Thanks for the reminder! 💧", "date": datetime.now().strftime("%Y-%m-%d"), "sid": "seed-d", "likes": 4, "replies": []}
                ]
            }
        ]
    }
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if CIRCLE_DATA_FILE.exists():
            with open(CIRCLE_DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, dict):
                data.setdefault("moods", default["moods"])
                data.setdefault("posts", default["posts"])
                return data
    except Exception:
        pass
    return default


def save_circle_data(data):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        temporary_file = CIRCLE_DATA_FILE.with_suffix(".tmp")
        with open(temporary_file, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        temporary_file.replace(CIRCLE_DATA_FILE)
        return True
    except Exception:
        return False


def circle_post_is_appropriate(text):
    cleaned = text.lower()
    blocked_terms = [
        "my phone number is", "my address is", "my password is",
        "my full name is", "my instagram is", "my snapchat is",
    ]
    return not any(term in cleaned for term in blocked_terms)


def organize_brain_dump(raw_text):
    chunks = [p.strip(" \t\r\n-•") for p in re.split(r"[\n,;]+|(?<=[.!?])\s+", raw_text) if p.strip(" \t\r\n-•")]
    buckets = {"URGENT": [], "THIS WEEK": [], "PERSONAL": [], "NOT IMPORTANT RIGHT NOW": []}

    personal_words = ("friend", "argument", "fight", "feel", "feeling", "thought", "upset", "family", "mom", "dad", "sad", "anxious", "counsellor", "counselor")
    urgent_words = ("tomorrow", "today", "tonight", "due", "unfinished", "overdue", "urgent", "now", "asap", "exam", "hours", "chaps", "chapter")
    week_words = ("next week", "this week", "project", "friday", "monday", "tuesday", "wednesday", "thursday", "study", "test", "end of the week")

    for item in chunks:
        lower = item.lower()
        if any(w in lower for w in personal_words):
            buckets["PERSONAL"].append(item)
        elif any(w in lower for w in urgent_words):
            buckets["URGENT"].append(item)
        elif any(w in lower for w in week_words):
            buckets["THIS WEEK"].append(item)
        else:
            buckets["NOT IMPORTANT RIGHT NOW"].append(item)
    return buckets


def get_resource_details(resource_title):
    details_map = {
        "understanding everyday stress": {
            "title": "Understanding Everyday Stress",
            "description": "Comprehensive resources to understand stress mechanics and build daily resilience.",
            "articles": [
                {"title": "What Is Stress & How to Handle It", "desc": "Understanding where stress comes from (Mind).", "url": "https://www.mind.org.uk/information-support/types-of-mental-health-problems/stress/"},
                {"title": "Anxiety: Ways to Ease Worry", "desc": "Simple, practical steps to calm anxious feelings (NHS).", "url": "https://www.nhs.uk/every-mind-matters/mental-health-issues/anxiety/"},
                {"title": "I'm So Stressed Out! Fact Sheet", "desc": "A teen-friendly guide to stress and coping (NIMH).", "url": "https://www.nimh.nih.gov/health/publications/so-stressed-out-fact-sheet"},
                {"title": "Stress Effects on the Body", "desc": "Recognizing the physical signs of pressure (APA).", "url": "https://www.apa.org/topics/stress/body"},
                {"title": "Stress Management Tools", "desc": "Everyday techniques that really help (HelpGuide).", "url": "https://www.helpguide.org/mental-health/stress/stress-management"}
            ],
            "videos": [
                {"title": "How to Make Stress Your Friend (Kelly McGonigal, TED)", "url": "https://www.youtube.com/watch?v=RcGyVTAoXEU", "thumb": "https://img.youtube.com/vi/RcGyVTAoXEU/hqdefault.jpg"},
                {"title": "All It Takes Is 10 Mindful Minutes (Andy Puddicombe, TED)", "url": "https://www.youtube.com/watch?v=qzR62JJCMBQ", "thumb": "https://img.youtube.com/vi/qzR62JJCMBQ/hqdefault.jpg"},
                {"title": "The Brain-Changing Benefits of Exercise (Wendy Suzuki, TED)", "url": "https://www.youtube.com/watch?v=BHY0FxzoKZE", "thumb": "https://img.youtube.com/vi/BHY0FxzoKZE/hqdefault.jpg"},
                {"title": "The Happy Secret to Better Work (Shawn Achor, TED)", "url": "https://www.youtube.com/watch?v=fLJsdqxnZb0", "thumb": "https://img.youtube.com/vi/fLJsdqxnZb0/hqdefault.jpg"},
                {"title": "How to Cope with Anxiety (Olivia Remes, TEDx)", "url": "https://www.youtube.com/watch?v=WWloIAQpMcQ", "thumb": "https://img.youtube.com/vi/WWloIAQpMcQ/hqdefault.jpg"}
            ],
            "books": [
                {"title": "The Mindful Teen", "author": "Dzung X. Vo", "image": "https://covers.openlibrary.org/b/isbn/1608823067-L.jpg", "amazon": "https://www.amazon.com/dp/1608823067"},
                {"title": "The Upside of Stress", "author": "Kelly McGonigal", "image": "https://covers.openlibrary.org/b/isbn/1583335617-L.jpg", "amazon": "https://www.amazon.com/dp/1583335617"},
                {"title": "Wherever You Go, There You Are", "author": "Jon Kabat-Zinn", "image": "https://covers.openlibrary.org/b/isbn/1401307787-L.jpg", "amazon": "https://www.amazon.com/dp/1401307787"},
                {"title": "Don't Sweat the Small Stuff", "author": "Richard Carlson", "image": "https://covers.openlibrary.org/b/isbn/0786881852-L.jpg", "amazon": "https://www.amazon.com/dp/0786881852"},
                {"title": "Why Zebras Don't Get Ulcers", "author": "Robert M. Sapolsky", "image": "https://covers.openlibrary.org/b/isbn/0805073698-L.jpg", "amazon": "https://www.amazon.com/dp/0805073698"}
            ]
        },
        "overcoming exam anxiety": {
            "title": "Overcoming Exam Anxiety",
            "description": "Targeted guides and tools to tackle test anxiety and feel calm under pressure.",
            "articles": [
                {"title": "Test Anxiety", "desc": "How to stay calm before and during tests (KidsHealth).", "url": "https://kidshealth.org/en/teens/test-anxiety.html"},
                {"title": "Exam Stress", "desc": "Practical tips for coping with exam pressure (YoungMinds).", "url": "https://www.youngminds.org.uk/young-person/coping-with-life/exam-stress/"},
                {"title": "Exam Stress: Ways to Cope", "desc": "Calming advice for revision and exam time (Childline).", "url": "https://www.childline.org.uk/info-advice/school-college-and-work/school-college/exam-stress/"},
                {"title": "Study Strategies That Work", "desc": "Evidence-based revision methods and free guides (Learning Scientists).", "url": "https://www.learningscientists.org/downloadable-materials"},
                {"title": "Learning How to Learn (Free Course)", "desc": "Build memory and study skills (Coursera).", "url": "https://www.coursera.org/learn/learning-how-to-learn"}
            ],
            "videos": [
                {"title": "How to Study for Exams: Evidence-Based Revision Tips (Ali Abdaal)", "url": "https://www.youtube.com/watch?v=ukLnPbIYi4g", "thumb": "https://img.youtube.com/vi/ukLnPbIYi4g/hqdefault.jpg"},
                {"title": "Learning How to Learn (Barbara Oakley, TEDx)", "url": "https://www.youtube.com/watch?v=O96fE1E-rf8", "thumb": "https://img.youtube.com/vi/O96fE1E-rf8/hqdefault.jpg"},
                {"title": "How to Stay Calm When You Know You'll Be Stressed (Daniel Levitin, TED)", "url": "https://www.youtube.com/watch?v=8jPQjjsBbIc", "thumb": "https://img.youtube.com/vi/8jPQjjsBbIc/hqdefault.jpg"},
                {"title": "Inside the Mind of a Master Procrastinator (Tim Urban, TED)", "url": "https://www.youtube.com/watch?v=arj7oStGLkU", "thumb": "https://img.youtube.com/vi/arj7oStGLkU/hqdefault.jpg"},
                {"title": "Sleep Is Your Superpower (Matt Walker, TED)", "url": "https://www.youtube.com/watch?v=5MuIMqhT8DM", "thumb": "https://img.youtube.com/vi/5MuIMqhT8DM/hqdefault.jpg"}
            ],
            "books": [
                {"title": "Make It Stick", "author": "Peter C. Brown, Henry L. Roediger III & Mark A. McDaniel", "image": "https://covers.openlibrary.org/b/isbn/0674729013-L.jpg", "amazon": "https://www.amazon.com/dp/0674729013"},
                {"title": "A Mind for Numbers", "author": "Barbara Oakley", "image": "https://covers.openlibrary.org/b/isbn/039916524X-L.jpg", "amazon": "https://www.amazon.com/dp/039916524X"},
                {"title": "How to Become a Straight-A Student", "author": "Cal Newport", "image": "https://covers.openlibrary.org/b/isbn/0767922719-L.jpg", "amazon": "https://www.amazon.com/dp/0767922719"},
                {"title": "Ultralearning", "author": "Scott H. Young", "image": "https://covers.openlibrary.org/b/isbn/0062852671-L.jpg", "amazon": "https://www.amazon.com/dp/0062852671"},
                {"title": "Why Don't Students Like School?", "author": "Daniel T. Willingham", "image": "https://covers.openlibrary.org/b/isbn/047059196X-L.jpg", "amazon": "https://www.amazon.com/dp/047059196X"}
            ]
        },
        "improving sleep quality": {
            "title": "Improving Sleep Quality",
            "description": "Proven sleep hygiene methods to wake up refreshed and focused.",
            "articles": [
                {"title": "Teens and Sleep", "desc": "How much sleep teens need and why it matters (Sleep Foundation).", "url": "https://www.sleepfoundation.org/teens-and-sleep"},
                {"title": "Sleep Hygiene", "desc": "Evening habits and routines for better sleep (Sleep Foundation).", "url": "https://www.sleepfoundation.org/sleep-hygiene"},
                {"title": "Sleep: Tips to Fall Asleep and Stay Asleep", "desc": "Practical help for restless nights (NHS).", "url": "https://www.nhs.uk/every-mind-matters/mental-health-issues/sleep/"},
                {"title": "Sleep Problems", "desc": "Understanding why sleep goes wrong (Mind).", "url": "https://www.mind.org.uk/information-support/types-of-mental-health-problems/sleep-problems/"},
                {"title": "Napping: Do's and Don'ts", "desc": "Power naps without wrecking night sleep (Mayo Clinic).", "url": "https://www.mayoclinic.org/healthy-lifestyle/adult-health/in-depth/napping/art-20048319"}
            ],
            "videos": [
                {"title": "Sleep Is Your Superpower (Matt Walker, TED)", "url": "https://www.youtube.com/watch?v=5MuIMqhT8DM", "thumb": "https://img.youtube.com/vi/5MuIMqhT8DM/hqdefault.jpg"},
                {"title": "Why School Should Start Later for Teens (Wendy Troxel, TED)", "url": "https://www.youtube.com/watch?v=TS6lFDVR-3g", "thumb": "https://img.youtube.com/vi/TS6lFDVR-3g/hqdefault.jpg"},
                {"title": "What Lack of Sleep Does to the Teenage Brain (TED-Ed)", "url": "https://www.youtube.com/watch?v=WJhCa12UTsg", "thumb": "https://img.youtube.com/vi/WJhCa12UTsg/hqdefault.jpg"},
                {"title": "What Would Happen If You Didn't Sleep? (TED-Ed)", "url": "https://www.youtube.com/watch?v=dqONk48l5vY", "thumb": "https://img.youtube.com/vi/dqONk48l5vY/hqdefault.jpg"}
            ],
            "books": [
                {"title": "Why We Sleep", "author": "Matthew Walker", "image": "https://covers.openlibrary.org/b/isbn/1501144316-L.jpg", "amazon": "https://www.amazon.com/dp/1501144316"},
                {"title": "Sleep Smarter", "author": "Shawn Stevenson", "image": "https://covers.openlibrary.org/b/isbn/1623367395-L.jpg", "amazon": "https://www.amazon.com/dp/1623367395"},
                {"title": "The Sleep Solution", "author": "W. Chris Winter", "image": "https://covers.openlibrary.org/b/isbn/0399583602-L.jpg", "amazon": "https://www.amazon.com/dp/0399583602"},
                {"title": "The Promise of Sleep", "author": "William C. Dement", "image": "https://covers.openlibrary.org/b/isbn/0440236738-L.jpg", "amazon": "https://www.amazon.com/dp/0440236738"},
                {"title": "Say Goodnight to Insomnia", "author": "Gregg D. Jacobs", "image": "https://covers.openlibrary.org/b/isbn/0805090835-L.jpg", "amazon": "https://www.amazon.com/dp/0805090835"}
            ]
        },
        "coping with sadness & loneliness": {
            "title": "Coping with Sadness & Loneliness",
            "description": "Gentle guides for low days, lonely moments and feeling better about yourself.",
            "articles": [
                {"title": "Depression (Teens)", "desc": "Understanding low mood and where to get help (KidsHealth).", "url": "https://kidshealth.org/en/teens/depression.html"},
                {"title": "Low Mood: Ways to Lift It", "desc": "Everyday steps to feel a little better (NHS).", "url": "https://www.nhs.uk/every-mind-matters/mental-health-issues/low-mood/"},
                {"title": "Feeling Lonely?", "desc": "Why loneliness happens and what can help (Childline).", "url": "https://www.childline.org.uk/info-advice/your-feelings/feelings/loneliness/"},
                {"title": "About Loneliness", "desc": "Ways to feel more connected (Mind).", "url": "https://www.mind.org.uk/information-support/tips-for-everyday-living/loneliness/about-loneliness/"},
                {"title": "Teen Depression Guide", "desc": "Signs, causes and treatment explained (NIMH).", "url": "https://www.nimh.nih.gov/health/publications/teen-depression"}
            ],
            "videos": [
                {"title": "What Makes a Good Life? Lessons from the Longest Study on Happiness (Robert Waldinger, TED)", "url": "https://www.youtube.com/watch?v=8KkKuTCFvzI", "thumb": "https://img.youtube.com/vi/8KkKuTCFvzI/hqdefault.jpg"},
                {"title": "The Power of Vulnerability (Brené Brown, TED)", "url": "https://www.youtube.com/watch?v=iCvmsMzlF7o", "thumb": "https://img.youtube.com/vi/iCvmsMzlF7o/hqdefault.jpg"},
                {"title": "Depression, the Secret We Share (Andrew Solomon, TED)", "url": "https://www.youtube.com/watch?v=eX2qFMC8cFo", "thumb": "https://img.youtube.com/vi/eX2qFMC8cFo/hqdefault.jpg"},
                {"title": "This Could Be Why You're Depressed or Anxious (Johann Hari, TED)", "url": "https://www.youtube.com/watch?v=PY9DcIMGxMs", "thumb": "https://img.youtube.com/vi/PY9DcIMGxMs/hqdefault.jpg"},
                {"title": "Brené Brown on Empathy (RSA Shorts)", "url": "https://www.youtube.com/watch?v=1Evwgu369Jw", "thumb": "https://img.youtube.com/vi/1Evwgu369Jw/hqdefault.jpg"}
            ],
            "books": [
                {"title": "Feeling Good", "author": "David D. Burns", "image": "https://covers.openlibrary.org/b/isbn/0380810336-L.jpg", "amazon": "https://www.amazon.com/dp/0380810336"},
                {"title": "Self-Compassion", "author": "Kristin Neff", "image": "https://covers.openlibrary.org/b/isbn/0061733520-L.jpg", "amazon": "https://www.amazon.com/dp/0061733520"},
                {"title": "The Gifts of Imperfection", "author": "Brené Brown", "image": "https://covers.openlibrary.org/b/isbn/159285849X-L.jpg", "amazon": "https://www.amazon.com/dp/159285849X"},
                {"title": "Lost Connections", "author": "Johann Hari", "image": "https://covers.openlibrary.org/b/isbn/163286830X-L.jpg", "amazon": "https://www.amazon.com/dp/163286830X"},
                {"title": "Man's Search for Meaning", "author": "Viktor E. Frankl", "image": "https://covers.openlibrary.org/b/isbn/080701429X-L.jpg", "amazon": "https://www.amazon.com/dp/080701429X"}
            ]
        },
        "friendships, bullying & peer pressure": {
            "title": "Friendships, Bullying & Peer Pressure",
            "description": "Handle bullying, cliques and friendship troubles, and build kinder connections.",
            "articles": [
                {"title": "Dealing With Bullying", "desc": "What to do if you or a friend is being bullied (KidsHealth).", "url": "https://kidshealth.org/en/teens/bullies.html"},
                {"title": "Cyberbullying", "desc": "Staying safe and responding to online bullying (KidsHealth).", "url": "https://kidshealth.org/en/teens/cyberbullying.html"},
                {"title": "Coping With Cliques", "desc": "Handling groups, belonging and peer pressure (KidsHealth).", "url": "https://kidshealth.org/en/teens/cliques.html"},
                {"title": "Being Assertive", "desc": "Say what you need clearly and kindly (KidsHealth).", "url": "https://kidshealth.org/en/teens/assertive.html"},
                {"title": "What Is Bullying?", "desc": "Facts, warning signs and how to get help (StopBullying.gov).", "url": "https://www.stopbullying.gov/bullying/what-is-bullying"}
            ],
            "videos": [
                {"title": "The Price of Shame (Monica Lewinsky, TED)", "url": "https://www.youtube.com/watch?v=H_8y0WLm78U", "thumb": "https://img.youtube.com/vi/H_8y0WLm78U/hqdefault.jpg"},
                {"title": "Brené Brown on Empathy (RSA Shorts)", "url": "https://www.youtube.com/watch?v=1Evwgu369Jw", "thumb": "https://img.youtube.com/vi/1Evwgu369Jw/hqdefault.jpg"},
                {"title": "10 Ways to Have a Better Conversation (Celeste Headlee, TED)", "url": "https://www.youtube.com/watch?v=R1vskiVDwl4", "thumb": "https://img.youtube.com/vi/R1vskiVDwl4/hqdefault.jpg"},
                {"title": "5 Ways to Listen Better (Julian Treasure, TED)", "url": "https://www.youtube.com/watch?v=cSohjlYQI2A", "thumb": "https://img.youtube.com/vi/cSohjlYQI2A/hqdefault.jpg"},
                {"title": "How to Speak So That People Want to Listen (Julian Treasure, TED)", "url": "https://www.youtube.com/watch?v=eIho2S0ZahI", "thumb": "https://img.youtube.com/vi/eIho2S0ZahI/hqdefault.jpg"}
            ],
            "books": [
                {"title": "Wonder", "author": "R. J. Palacio", "image": "https://covers.openlibrary.org/b/isbn/0375869026-L.jpg", "amazon": "https://www.amazon.com/dp/0375869026"},
                {"title": "How to Win Friends and Influence People", "author": "Dale Carnegie", "image": "https://covers.openlibrary.org/b/isbn/0671027034-L.jpg", "amazon": "https://www.amazon.com/dp/0671027034"},
                {"title": "Quiet", "author": "Susan Cain", "image": "https://covers.openlibrary.org/b/isbn/0307352153-L.jpg", "amazon": "https://www.amazon.com/dp/0307352153"},
                {"title": "The 7 Habits of Highly Effective Teens", "author": "Sean Covey", "image": "https://covers.openlibrary.org/b/isbn/0684856093-L.jpg", "amazon": "https://www.amazon.com/dp/0684856093"},
                {"title": "Daring Greatly", "author": "Brené Brown", "image": "https://covers.openlibrary.org/b/isbn/1592408419-L.jpg", "amazon": "https://www.amazon.com/dp/1592408419"}
            ]
        },
        "focus, motivation & screen time": {
            "title": "Focus, Motivation & Screen Time",
            "description": "Beat procrastination, build small habits and take back your attention.",
            "articles": [
                {"title": "The 2-Minute Rule", "desc": "Stop procrastinating by starting tiny (James Clear).", "url": "https://jamesclear.com/stop-procrastinating-2-minute-rule"},
                {"title": "Habits: The Complete Guide", "desc": "How to build habits that stick (James Clear).", "url": "https://jamesclear.com/habits"},
                {"title": "The Pomodoro Technique", "desc": "Work in short, focused bursts with breaks (Todoist).", "url": "https://todoist.com/productivity-methods/pomodoro-technique"},
                {"title": "Exercise: 7 Benefits of Regular Activity", "desc": "Move to boost mood, energy and focus (Mayo Clinic).", "url": "https://www.mayoclinic.org/healthy-lifestyle/fitness/in-depth/exercise/art-20048389"},
                {"title": "How to Make a Family Media Use Plan", "desc": "Balance screen time and real life (HealthyChildren.org).", "url": "https://www.healthychildren.org/English/family-life/Media/Pages/How-to-Make-a-Family-Media-Use-Plan.aspx"}
            ],
            "videos": [
                {"title": "Inside the Mind of a Master Procrastinator (Tim Urban, TED)", "url": "https://www.youtube.com/watch?v=arj7oStGLkU", "thumb": "https://img.youtube.com/vi/arj7oStGLkU/hqdefault.jpg"},
                {"title": "How to Stop Screwing Yourself Over (Mel Robbins, TEDx)", "url": "https://www.youtube.com/watch?v=Lp7E973zozc", "thumb": "https://img.youtube.com/vi/Lp7E973zozc/hqdefault.jpg"},
                {"title": "Grit: The Power of Passion and Perseverance (Angela Duckworth, TED)", "url": "https://www.youtube.com/watch?v=H14bBuluwB8", "thumb": "https://img.youtube.com/vi/H14bBuluwB8/hqdefault.jpg"},
                {"title": "The Power of Believing That You Can Improve (Carol Dweck, TEDx)", "url": "https://www.youtube.com/watch?v=_X0mgOOSpLU", "thumb": "https://img.youtube.com/vi/_X0mgOOSpLU/hqdefault.jpg"},
                {"title": "Why You Should Quit Social Media (Cal Newport, TEDx)", "url": "https://www.youtube.com/watch?v=3E7hkPZ-HTk", "thumb": "https://img.youtube.com/vi/3E7hkPZ-HTk/hqdefault.jpg"}
            ],
            "books": [
                {"title": "Atomic Habits", "author": "James Clear", "image": "https://covers.openlibrary.org/b/isbn/0735211299-L.jpg", "amazon": "https://www.amazon.com/dp/0735211299"},
                {"title": "Deep Work", "author": "Cal Newport", "image": "https://covers.openlibrary.org/b/isbn/1455586692-L.jpg", "amazon": "https://www.amazon.com/dp/1455586692"},
                {"title": "Grit", "author": "Angela Duckworth", "image": "https://covers.openlibrary.org/b/isbn/1501111108-L.jpg", "amazon": "https://www.amazon.com/dp/1501111108"},
                {"title": "Mindset", "author": "Carol S. Dweck", "image": "https://covers.openlibrary.org/b/isbn/0345472322-L.jpg", "amazon": "https://www.amazon.com/dp/0345472322"},
                {"title": "Digital Minimalism", "author": "Cal Newport", "image": "https://covers.openlibrary.org/b/isbn/0525536515-L.jpg", "amazon": "https://www.amazon.com/dp/0525536515"}
            ]
        }
    }

    key = str(resource_title).lower().strip()
    if key in details_map:
        return details_map[key]

    return {
        "title": resource_title,
        "description": f"Curated guides, videos, and books for {resource_title}.",
        "articles": [
            {"title": f"Complete Guide to {resource_title}", "desc": "Understanding key principles and daily steps.", "url": "https://www.mentalhealth.org.uk/"},
            {"title": f"Managing Daily {resource_title}", "desc": "Practical coping strategies.", "url": "https://www.mind.org.uk/"},
            {"title": f"Student Wellness & {resource_title}", "desc": "Balancing school and wellbeing.", "url": "https://www.kidshealth.org/"},
            {"title": f"Recognizing Triggers for {resource_title}", "desc": "Awareness techniques.", "url": "https://www.apa.org/"},
            {"title": f"Building Resilience in {resource_title}", "desc": "Long-term habits.", "url": "https://www.helpguide.org/"}
        ],
        "videos": [
            {"title": f"Understanding {resource_title}", "url": "https://www.youtube.com/watch?v=hnpQrMqDoqE", "thumb": "https://img.youtube.com/vi/hnpQrMqDoqE/0.jpg"},
            {"title": f"Top 5 Tips for {resource_title}", "url": "https://www.youtube.com/watch?v=inpok4MKVLM", "thumb": "https://img.youtube.com/vi/inpok4MKVLM/0.jpg"},
            {"title": f"Mindfulness for {resource_title}", "url": "https://www.youtube.com/watch?v=fAJifi62pDY", "thumb": "https://img.youtube.com/vi/fAJifi62pDY/0.jpg"},
            {"title": f"Guided Exercise for {resource_title}", "url": "https://www.youtube.com/watch?v=2Lz0VOltZKA", "thumb": "https://img.youtube.com/vi/2Lz0VOltZKA/0.jpg"},
            {"title": f"Expert Insights on {resource_title}", "url": "https://www.youtube.com/watch?v=nm1g9qjCxnE", "thumb": "https://img.youtube.com/vi/nm1g9qjCxnE/0.jpg"}
        ],
        "books": [
            {"title": "The Mindfulness Journal for Teens", "author": "Jennie Marie Battistin", "image": "https://images-na.ssl-images-amazon.com/images/I/71oD410-z6L.jpg", "amazon": "https://www.amazon.com/dp/1641524385"},
            {"title": "The Anxiety Workbook for Teens", "author": "Lisa M. Schab", "image": "https://images-na.ssl-images-amazon.com/images/I/81v6X0W8LcL.jpg", "amazon": "https://www.amazon.com/dp/1567318464"},
            {"title": "Don't Sweat the Small Stuff", "author": "Richard Carlson", "image": "https://images-na.ssl-images-amazon.com/images/I/71u9c7+5YKL.jpg", "amazon": "https://www.amazon.com/dp/0101700021"},
            {"title": "Mindset: The New Psychology of Success", "author": "Carol S. Dweck", "image": "https://images-na.ssl-images-amazon.com/images/I/81g7w+9c-rL.jpg", "amazon": "https://www.amazon.com/dp/0345472322"},
            {"title": "Atomic Habits", "author": "James Clear", "image": "https://images-na.ssl-images-amazon.com/images/I/71+vR5B5+WL.jpg", "amazon": "https://www.amazon.com/dp/0735211299"}
        ],
    }


def get_activity_guidance(activity_name, description):
    guides = {
        "1-minute breathing reset": [
            "Sit comfortably and gently relax your shoulders.",
            "Breathe in quietly through your nose for 4 seconds.",
            "Hold your breath softly for 2 seconds.",
            "Exhale slowly through your mouth for 6 seconds.",
            "Repeat until the timer completes.",
        ],
        "5-minute brain dump": [
            "Take a piece of paper or open a blank note.",
            "Write down every single thought or worry on your mind.",
            "Don't filter or edit—just let it all flow out.",
            "Pick just ONE small step you can address today.",
        ],
        "grounding check-in": [
            "Look around your room and name 5 things you can see.",
            "Notice and touch 4 physical things around you.",
            "Listen carefully and identify 3 distinct sounds.",
            "Identify 2 things you can smell or enjoy smelling.",
            "Take 1 deep, calm breath.",
        ],
        "box breathing": [
            "Sit upright and relax your shoulders.",
            "Breathe in slowly through your nose for 4 seconds.",
            "Hold your breath gently for 4 seconds.",
            "Breathe out slowly through your mouth for 4 seconds.",
            "Hold the empty breath for 4 seconds, then repeat the square.",
        ],
        "neck & shoulder release": [
            "Sit tall and drop your shoulders away from your ears.",
            "Slowly tilt your right ear toward your right shoulder and breathe for 15 seconds.",
            "Switch sides and repeat gently.",
            "Roll your shoulders backward 5 times, then forward 5 times.",
            "Interlace your fingers, stretch your arms forward and take a deep breath.",
        ],
        "three good things": [
            "Pause and take one slow breath.",
            "Think of one small good thing from today (a snack, a laugh, a kind word).",
            "Think of a second good thing, however tiny.",
            "Think of a third, maybe something about yourself.",
            "Smile gently and notice how your body feels now.",
        ],
        "body scan relaxation": [
            "Sit or lie down comfortably and close your eyes if you like.",
            "Bring attention to your forehead and jaw, and let them soften.",
            "Move to your neck, shoulders and arms, releasing any tightness.",
            "Notice your chest and belly rising and falling with each breath.",
            "Relax your legs and feet, then take one big, slow breath.",
        ],
        "mindful water break": [
            "Pour or pick up a glass of water.",
            "Notice the temperature and the weight of the glass.",
            "Take slow sips and feel the water move down.",
            "Take 3 calm breaths before returning to what you were doing.",
        ],
    }
    name_lower = str(activity_name).lower().strip()
    steps = guides.get(name_lower)
    if not steps:
        steps = [
            f"Take a moment to pause and focus: {description}",
            "Follow along gently at your own comfortable pace.",
            "Use the timer below to give yourself a focused break.",
        ]
    return steps


def generate_conversational_reply(user_text, history):
    text = user_text.lower()

    if any(k in text for k in ["don't suggest", "dont suggest", "no activity", "no activities", "just talk", "stop suggesting"]):
        st.session_state.suppress_activities = True
        return "Got it! I won't suggest any activities or exercises. I'm right here to just listen and talk. What's on your mind?"

    if any(k in text for k in ["hi", "hello", "hey", "sup", "yo"]):
        return random.choice([
            "Hey there! I'm Mino 🌿 How are you holding up today?",
            "Hello! Glad you reached out. What's on your mind right now?",
            "Hey! I'm right here with you. How has your day been treating you so far?"
        ])
    elif any(k in text for k in ["exam", "test", "study", "studying", "chapter", "chaps", "subject", "homework", "assignment", "accounts"]):
        return random.choice([
            "Academic pressure can get really overwhelming. Is there a specific subject or topic causing the most stress right now?",
            "Studying when your mind is racing is tough. Are you trying to cram for something coming up soon?",
            "I hear you. Taking things one task at a time really helps. What's the main thing on your plate today?"
        ])
    elif any(k in text for k in ["friend", "friends", "argument", "fight", "relationship", "counsellor", "counselor"]):
        return random.choice([
            "Friend and personal stuff can sit heavily on your mind all day long. Do you want to vent about what happened?",
            "Social stress is genuinely exhausting. Was this an unexpected situation, or something building up for a while?",
            "I'm listening carefully. What's bothering you most about it?"
        ])
    elif any(k in text for k in ["tired", "sleep", "exhausted", "burnout", "drain"]):
        return random.choice([
            "Feeling drained makes everything else feel ten times harder. Have you been able to rest properly lately?",
            "Sounds like you're running on empty. What's been taking up most of your energy today?",
            "Rest is just as important as getting things done. Are you able to take a breather right now?"
        ])
    elif any(k in text for k in ["sad", "low", "upset", "cry", "lonely"]):
        return random.choice([
            "I'm sorry you're feeling down. You don't have to carry it all alone—what's making you feel this way today?",
            "It's completely okay to feel like this sometimes. I'm right here with you. Do you want to talk it through?",
            "Sending you a gentle hug 🌿 What feels like the heaviest part of everything right now?"
        ])
    elif any(k in text for k in ["stressed", "overwhelmed", "anxious", "panic", "scared"]):
        return random.choice([
            "When everything hits at once, it's really easy to feel overwhelmed. What's the number one thing stressing you out right now?",
            "Take a slow breath with me. We can tackle things one by one. What feels like the main priority?",
            "I hear how much pressure you're under. Let's talk through it step by step."
        ])
    else:
        return random.choice([
            "That sounds like a lot to process. How are you coping with all of that right now?",
            "I really hear where you're coming from. What do you think would help you feel even a little bit lighter today?",
            "Thanks for sharing that with me. What part of this situation feels like it's in your control right now?"
        ])


def get_response_for_intent(intent):
    if responses_df.empty:
        return "I'm listening and right here with you. How are you holding up with everything?", None
    try:
        matches = responses_df[
            responses_df["Intent_ID"].astype(str).str.strip() == str(intent).strip()
        ]
    except Exception:
        matches = pd.DataFrame()

    if matches.empty:
        return "I hear you. Tell me a bit more about what's going on—I'm listening.", None

    row = matches.iloc[0]
    response = safe_text(row.get("Response"), "I hear you. Tell me a bit more about what's on your mind.")
    activity_id = clean_value(row.get("Activity_ID"))
    return response, activity_id


def get_activity(activity_id):
    if not activity_id or activities_df.empty:
        return None
    try:
        matches = activities_df[
            activities_df["Activity_ID"].astype(str).str.strip() == str(activity_id).strip()
        ]
        return matches.iloc[0] if not matches.empty else None
    except Exception:
        return None


def activity_name(activity):
    if activity is None:
        return "A small reset"
    for col in ["Activity_Name", "Name", "Activity", "Title"]:
        if col in activity.index:
            val = clean_value(activity[col])
            if val:
                return val
    return "A small reset"


def activity_description(activity):
    if activity is None:
        return ""
    for col in ["Description", "Activity_Description", "Instructions"]:
        if col in activity.index:
            val = clean_value(activity[col])
            if val:
                return val
    return ""


def activity_duration(activity):
    if activity is None:
        return 1
    for col in ["Duration_Min", "Duration", "Time"]:
        if col in activity.index:
            val = clean_value(activity[col])
            if val:
                try:
                    return int(val)
                except ValueError:
                    pass
    return 1


def go_to(page):
    st.session_state.page = page


# ------------------------------------------------------------
# 4b. MINI-GAME GENERATORS (every game reshuffles with new levels)
# ------------------------------------------------------------

MEMORY_EMOJIS = ["🌸", "🌿", "🌊", "☀️", "🦋", "🍃", "🌙", "⭐", "🍀", "🐚", "🌻", "🍓", "🦉", "🐢", "🌈", "🍉"]

SCRAMBLE_WORDS = [
    "SERENE", "BREATHE", "PEACEFUL", "RELAX", "HARMONY", "GENTLE", "SUNSHINE", "BALANCE",
    "COMFORT", "GRATEFUL", "TRANQUIL", "BLOSSOM", "MINDFUL", "COZY", "SMILE", "RESTFUL",
    "KINDNESS", "SOOTHE", "BREEZE", "MEADOW",
]

EMOJI_FLOWS = [
    (["🥚", "🐣"], "🐥"),
    (["🌱", "🌿"], "🌳"),
    (["🌑", "🌓"], "🌕"),
    (["☁️", "🌧️"], "🌈"),
    (["🌅", "☀️"], "🌇"),
    (["🧒", "🧑"], "🧓"),
    (["🌙", "⭐"], "☀️"),
    (["🌰", "🌱"], "🌲"),
]
EMOJI_DECOYS = ["☁️", "🌸", "🍎", "🚗", "🐟", "🎈", "🌊", "🍕", "🔥", "❄️", "🎵", "🍩"]

ODD_GROUPS = {
    "fruit": ["🍎", "🍊", "🍋", "🍇", "🍓", "🍌", "🍉"],
    "animals": ["🐶", "🐱", "🐰", "🐼", "🦊", "🐸"],
    "flowers": ["🌸", "🌻", "🌷", "🌹", "🌼", "🪻"],
    "transport": ["🚗", "🚌", "🚲", "✈️", "🚂", "⛵"],
    "weather": ["☀️", "🌧️", "⛈️", "❄️", "🌈", "💨"],
    "sweets": ["🍩", "🍪", "🍰", "🍫", "🍦", "🧁"],
}

CROSSWORD_WORDS = [
    "CALM", "HOPE", "REST", "PEACE", "BREATHE", "SMILE", "KIND", "GROW", "FOCUS", "JOY",
    "TRUST", "LIGHT", "SERENE", "RELAX", "HEAL", "BLOOM", "DREAM", "SAFE", "BRAVE", "QUIET",
    "GENTLE", "STRONG", "HAPPY", "SUNNY", "BALANCE", "COZY", "BREEZE", "MINDFUL", "HAVEN", "GLOW",
]


def new_memory_game():
    level = st.session_state.memory_level
    pairs = min(5 + level, 10)
    cards = random.sample(MEMORY_EMOJIS, pairs) * 2
    random.shuffle(cards)
    st.session_state.memory_cards = cards
    st.session_state.memory_flipped = []
    st.session_state.memory_matched = []
    st.session_state.memory_moves = 0


def new_scramble():
    previous = st.session_state.scramble_word
    chosen = random.choice([w for w in SCRAMBLE_WORDS if w != previous])
    jumbled = list(chosen)
    for _ in range(25):
        random.shuffle(jumbled)
        if "".join(jumbled) != chosen:
            break
    st.session_state.scramble_word = chosen
    st.session_state.scramble_jumbled = "".join(jumbled)
    st.session_state.scramble_round += 1


def new_pattern():
    kind = random.choice(["add", "sub", "mul", "square", "grow", "fib"])
    if kind == "add":
        s, d = random.randint(1, 9), random.randint(2, 7)
        seq = [s + d * i for i in range(5)]
        hint = f"Each number goes up by {d}."
    elif kind == "sub":
        s, d = random.randint(30, 50), random.randint(2, 6)
        seq = [s - d * i for i in range(5)]
        hint = f"Each number goes down by {d}."
    elif kind == "mul":
        s, r = random.randint(1, 3), random.choice([2, 3])
        seq = [s * r ** i for i in range(5)]
        hint = f"Each number is multiplied by {r}."
    elif kind == "square":
        o = random.randint(0, 3)
        seq = [(i + 1 + o) ** 2 for i in range(5)]
        hint = "These are square numbers (1×1, 2×2, 3×3...)."
    elif kind == "grow":
        seq = [random.randint(1, 5)]
        step = 1
        for _ in range(4):
            seq.append(seq[-1] + step)
            step += 1
        hint = "The jump gets bigger by 1 each time."
    else:
        a, b = random.randint(1, 3), random.randint(1, 4)
        seq = [a, b]
        while len(seq) < 5:
            seq.append(seq[-1] + seq[-2])
        hint = "Add the two previous numbers together."
    st.session_state.pattern_seq = seq[:4]
    st.session_state.pattern_answer = seq[4]
    st.session_state.pattern_hint = hint
    st.session_state.pattern_round += 1


def new_emoji():
    previous = tuple(st.session_state.emoji_seq)
    choices = [f for f in EMOJI_FLOWS if tuple(f[0]) != previous]
    seq, answer = random.choice(choices)
    decoys = random.sample([d for d in EMOJI_DECOYS if d != answer and d not in seq], 2)
    options = [answer] + decoys
    random.shuffle(options)
    st.session_state.emoji_seq = list(seq)
    st.session_state.emoji_answer = answer
    st.session_state.emoji_options = options
    st.session_state.emoji_round += 1


def new_odd():
    g1, g2 = random.sample(list(ODD_GROUPS), 2)
    items = random.sample(ODD_GROUPS[g1], 3)
    odd = random.choice(ODD_GROUPS[g2])
    items.append(odd)
    random.shuffle(items)
    st.session_state.odd_items = items
    st.session_state.odd_answer = odd
    st.session_state.odd_round += 1


def new_wordsearch():
    level = st.session_state.crossword_level
    n = min(6 + level, 10)
    count = min(3 + level, 6)
    dirs = [(0, 1), (1, 0)]
    if level >= 2:
        dirs.append((1, 1))
    if level >= 3:
        dirs += [(0, -1), (-1, 0)]

    grid, placed = None, []
    for _ in range(60):
        words = random.sample([w for w in CROSSWORD_WORDS if len(w) <= n], count)
        trial = [[""] * n for _ in range(n)]
        trial_placed = []
        for w in sorted(words, key=len, reverse=True):
            for _ in range(120):
                dr, dc = random.choice(dirs)
                r, c = random.randrange(n), random.randrange(n)
                er, ec = r + dr * (len(w) - 1), c + dc * (len(w) - 1)
                if not (0 <= er < n and 0 <= ec < n):
                    continue
                cells = [(r + dr * i, c + dc * i) for i in range(len(w))]
                if all(trial[a][b] in ("", w[i]) for i, (a, b) in enumerate(cells)):
                    for i, (a, b) in enumerate(cells):
                        trial[a][b] = w[i]
                    trial_placed.append(w)
                    break
        grid, placed = trial, trial_placed
        if len(trial_placed) == count:
            break

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for r in range(n):
        for c in range(n):
            if grid[r][c] == "":
                grid[r][c] = random.choice(letters)

    st.session_state.crossword_grid = ["".join(row) for row in grid]
    st.session_state.crossword_words = placed
    st.session_state.crossword_found_words = []
    st.session_state.crossword_segments = []
    st.session_state.crossword_last_nonce = None
    st.session_state.crossword_round += 1


def game_say(game, kind, text):
    st.session_state.game_feedback[game] = (kind, text)


def game_feedback_show(game):
    fb = st.session_state.game_feedback.pop(game, None)
    if fb:
        if fb[0] == "ok":
            st.success(fb[1])
        else:
            st.info(fb[1])


# ------------------------------------------------------------
# 4c. MINDMATE CIRCLE (SOCIAL FEED) HELPERS
# ------------------------------------------------------------

CIRCLE_AVATARS = [
    ("🐼", "Panda", "#E8F1EA"), ("🦊", "Fox", "#FCE9DF"), ("🐨", "Koala", "#E9EEF6"),
    ("🐧", "Penguin", "#E6EEF3"), ("🦉", "Owl", "#F3ECDD"), ("🐢", "Turtle", "#E3F1E4"),
    ("🦋", "Butterfly", "#EDE6F5"), ("🐰", "Bunny", "#F8E8EE"), ("🦦", "Otter", "#EFE7DF"),
    ("🐙", "Octopus", "#F8E6E6"), ("🦔", "Hedgehog", "#EDE9E1"), ("🐝", "Bee", "#FBF1D3"),
]
CIRCLE_ADJECTIVES = ["Calm", "Kind", "Brave", "Gentle", "Sunny", "Cozy", "Quiet", "Bright", "Steady", "Hopeful"]


def circle_identity(seed):
    value = zlib.crc32(str(seed).encode("utf-8"))
    emoji, animal, color = CIRCLE_AVATARS[value % len(CIRCLE_AVATARS)]
    adjective = CIRCLE_ADJECTIVES[(value // 7) % len(CIRCLE_ADJECTIVES)]
    return emoji, f"{adjective} {animal}", color


def circle_time_label(item):
    ts = item.get("ts")
    if ts:
        try:
            diff = max(0, int(time.time() - float(ts)))
            if diff < 60:
                return "Just now"
            if diff < 3600:
                return f"{diff // 60}m ago"
            if diff < 86400:
                return f"{diff // 3600}h ago"
        except Exception:
            pass
    return item.get("date", "")


def _circle_find(data, post_id, cid=None, rid=None):
    for post in data.get("posts", []):
        if post.get("id") != post_id:
            continue
        if cid is None:
            return post
        for comment in post.get("comments", []):
            if comment.get("id") != cid:
                continue
            if rid is None:
                return comment
            for reply in comment.get("replies", []):
                if reply.get("id") == rid:
                    return reply
    return None


def circle_toggle_like(post_id, cid=None, rid=None, reaction=None):
    data = load_circle_data()
    target = _circle_find(data, post_id, cid, rid)
    if target is None:
        return
    token = f"{post_id}|{cid}|{rid}|{reaction}"
    liked = st.session_state.circle_liked
    if reaction:
        store = target.setdefault("reactions", {})
        field = reaction
    else:
        store = target
        field = "likes"
    current = int(store.get(field, 0))
    if token in liked:
        liked.discard(token)
        store[field] = max(0, current - 1)
    else:
        liked.add(token)
        store[field] = current + 1
    save_circle_data(data)


def circle_toggle_comments(post_id):
    opened = st.session_state.circle_open_comments
    if post_id in opened:
        opened.discard(post_id)
    else:
        opened.add(post_id)


def circle_add_comment(post_id):
    key = f"cmt_in_{post_id}"
    text = str(st.session_state.get(key, "")).strip()
    if not text or not circle_post_is_appropriate(text):
        return
    data = load_circle_data()
    post = _circle_find(data, post_id)
    if post is None:
        return
    post.setdefault("comments", []).append({
        "id": f"C-{int(time.time() * 1000)}",
        "text": text[:240],
        "ts": time.time(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "sid": st.session_state.student_id,
        "likes": 0,
        "replies": [],
    })
    save_circle_data(data)
    st.session_state[key] = ""


def circle_start_reply(post_id, cid):
    st.session_state.circle_reply_to = f"{post_id}|{cid}"


def circle_add_reply(post_id, cid):
    key = f"reply_in_{cid}"
    text = str(st.session_state.get(key, "")).strip()
    if not text or not circle_post_is_appropriate(text):
        return
    data = load_circle_data()
    comment = _circle_find(data, post_id, cid)
    if comment is None:
        return
    comment.setdefault("replies", []).append({
        "id": f"R-{int(time.time() * 1000)}",
        "text": text[:240],
        "ts": time.time(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "sid": st.session_state.student_id,
        "likes": 0,
    })
    save_circle_data(data)
    st.session_state.circle_reply_to = None


def circle_comment_html(item, indent=False):
    emoji, alias, color = circle_identity(item.get("sid") or item.get("id", "x"))
    you = ' <span class="cp-you">You</span>' if item.get("sid") and item.get("sid") == st.session_state.student_id else ""
    body = escape(item.get("text", "")).replace("\n", "<br>")
    cls = "cm-row cm-reply" if indent else "cm-row"
    return (
        f'<div class="{cls}"><div class="cm-avatar" style="background:{color}">{emoji}</div>'
        f'<div class="cm-bubble"><div class="cm-name">{escape(alias)}{you} <span class="cp-time">· {escape(circle_time_label(item))}</span></div>'
        f'<div class="cm-text">{body}</div></div></div>'
    )


# ------------------------------------------------------------
# 4d. BRAIN DUMP RECORDS (SAVED TO THE LEFT SIDEBAR)
# ------------------------------------------------------------

def derive_record_name(result, raw_text):
    stop = {"the", "my", "an", "a", "for", "this", "next", "have", "has", "got", "our", "your", "that",
            "final", "big", "and", "to", "in", "of", "is", "are", "i", "me", "need", "do", "with"}
    pattern = r"\b([A-Za-z][A-Za-z&]{2,})\s+(exam|test|quiz|assignment|project|homework|practical|presentation)\b"
    for match in re.finditer(pattern, raw_text or "", re.IGNORECASE):
        subject = match.group(1)
        if subject.lower() not in stop:
            return f"{subject.title()} {match.group(2).lower()}"
    for bucket in ("URGENT", "THIS WEEK", "PERSONAL", "NOT IMPORTANT RIGHT NOW"):
        items = result.get(bucket, [])
        if items:
            text = items[0].strip()
            return text if len(text) <= 38 else text[:36].rstrip() + "…"
    return f"Brain dump {datetime.now().strftime('%d %b')}"


def save_dump_record(result, plan):
    record = {
        "id": f"BD-{int(time.time() * 1000)}",
        "name": derive_record_name(result, st.session_state.get("brain_dump_raw", "")),
        "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "result": result,
        "plan": plan,
    }
    st.session_state.dump_records.append(record)
    append_to_excel("10_Brain_Dump_Records", {
        "Record_ID": record["id"],
        "Student_ID": st.session_state.student_id,
        "Date": record["date"],
        "Name": record["name"],
        "Difficulty": plan.get("difficulty"),
        "Time_Available": plan.get("time"),
        "Items_Total": sum(len(v) for v in result.values()),
        "Steps_Completed": len(plan.get("steps", [])),
    })
    return record



# ------------------------------------------------------------
# 4e. SMART CHAT ENGINE (context-aware replies, resources, human support)
# ------------------------------------------------------------

SEVERE_PHRASES = [
    "kill myself", "suicide", "suicidal", "end my life", "want to die", "wanna die", "better off dead",
    "hurt myself", "harm myself", "self harm", "self-harm", "cut myself", "cutting myself",
    "no reason to live", "don't want to live", "dont want to live", "end it all", "can't go on",
    "cant go on", "not worth living", "don't want to be here", "dont want to be here", "disappear forever",
]

HIGH_PHRASES = [
    "can't cope", "cant cope", "breaking down", "breakdown", "panic attack", "can't breathe", "cant breathe",
    "can't take it", "cant take it", "too much to handle", "hate myself", "worthless", "hopeless",
    "no one cares", "nobody cares", "i give up", "falling apart", "can't do this anymore", "cant do this anymore",
    "can't handle", "cant handle", "everything is too much",
]

STRESS_WORDS = [
    "stress*", "anxious", "anxiety", "overwhelm*", "panic*", "worr*", "scared", "afraid", "nervous",
    "pressure", "burnout", "burnt out", "exhausted", "sad", "lonely", "depress*", "cry*", "upset", "tense",
    "overthink*", "frustrat*", "can't study", "cant study", "can't focus", "cant focus",
]

TOPIC_KEYWORDS = {
    "exam": ["exam*", "test", "tests", "quiz", "finals", "boards", "marks", "grades", "results", "revision",
             "revise", "syllabus", "chapter*", "chaps", "study", "studying", "homework", "assignment*",
             "deadline*", "project", "accounts", "maths", "math", "science", "preparation"],
    "sleep": ["sleep*", "insomnia", "tired", "exhausted", "nap", "awake", "bedtime", "burnout", "burnt out"],
    "friends": ["friend*", "bestie", "argument", "fight", "fought", "ignored", "left out", "bully", "bullied",
                "bullying", "classmate*", "peer*"],
    "family": ["parent*", "mom", "dad", "mother", "father", "family", "sibling*", "brother", "sister"],
    "lonely": ["lonely", "alone", "isolated", "nobody", "no one", "no friends"],
    "sad": ["sad", "down", "low", "cry*", "depressed", "empty", "numb", "unhappy", "upset", "miserable"],
    "anxious": ["anxious", "anxiety", "nervous", "panic*", "worr*", "scared", "afraid", "fear", "overthink*",
                "tense", "uneasy"],
    "overwhelmed": ["overwhelm*", "too much", "stress*", "pressure", "swamped", "can't keep up", "cant keep up"],
    "anger": ["angry", "mad", "furious", "annoyed", "frustrat*", "irritated", "rage"],
    "motivation": ["unmotivated", "motivation", "procrastinat*", "lazy", "focus", "distracted", "bored",
                   "can't start", "cant start", "don't feel like", "dont feel like"],
    "selfesteem": ["not good enough", "stupid", "failure", "loser", "ugly", "compare", "comparing",
                   "insecure", "hate myself", "dumb", "worthless"],
    "phone": ["phone", "instagram", "scrolling", "reels", "social media", "youtube", "gaming", "addicted"],
}

DISTRESS_TOPICS = {"anxious", "overwhelmed", "sad", "lonely", "selfesteem"}

RESOURCE_MAP = {
    # "key" = which resource set to use. "start" (optional) = which article / video to show first,
    # so each concern gets the most fitting item for that exact worry.
    "exam": {
        "key": "Overcoming Exam Anxiety",
        "article": "You could refer to this article for managing exam stress",
        "video": "This video might help you feel calmer before your exam",
    },
    "sleep": {
        "key": "Improving Sleep Quality",
        "article": "This article has simple tips for sleeping better",
        "video": "This video might help you wind down for better sleep",
    },
    "anxious": {
        "key": "Understanding Everyday Stress",
        "start": {"article": 1, "video": 4},
        "article": "You could read this article to understand and handle anxious feelings",
        "video": "This video might help you cope with anxious feelings",
    },
    "overwhelmed": {
        "key": "Understanding Everyday Stress",
        "start": {"article": 0, "video": 0},
        "article": "You could refer to this article for managing everyday stress",
        "video": "This video might help you relax and slow down",
    },
    "sad": {
        "key": "Coping with Sadness & Loneliness",
        "start": {"article": 0, "video": 2},
        "article": "This article on coping with heavy feelings might help",
        "video": "This video might help when everything feels heavy",
    },
    "lonely": {
        "key": "Coping with Sadness & Loneliness",
        "start": {"article": 2, "video": 0},
        "article": "This article on feeling lonely might help",
        "video": "This video is about why connection matters, it might help",
    },
    "selfesteem": {
        "key": "Coping with Sadness & Loneliness",
        "start": {"article": 1, "video": 1},
        "article": "This article on lifting a low mood might help",
        "video": "This video on being yourself might help you feel more worthy",
    },
    "friends": {
        "key": "Friendships, Bullying & Peer Pressure",
        "start": {"article": 0, "video": 1},
        "article": "You could refer to this article for handling friend and peer problems",
        "video": "This video might help you handle people and feelings better",
    },
    "family": {
        "key": "Understanding Everyday Stress",
        "start": {"article": 4, "video": 3},
        "article": "You could refer to this article for handling pressure",
        "video": "This video might help you feel lighter",
    },
    "anger": {
        "key": "Understanding Everyday Stress",
        "start": {"article": 3, "video": 1},
        "article": "You could refer to this article to understand what stress does to your body",
        "video": "This video might help you cool down",
    },
    "motivation": {
        "key": "Focus, Motivation & Screen Time",
        "start": {"article": 0, "video": 0},
        "article": "You could refer to this article for getting started when you feel stuck",
        "video": "This video might help you reset and refocus",
    },
    "phone": {
        "key": "Focus, Motivation & Screen Time",
        "start": {"article": 4, "video": 4},
        "article": "This article might help you balance screen time",
        "video": "This video might help you take back your focus",
    },
}

# stage 0 = first time this topic comes up, 1 = second time, 2 = after that.
# {d} is replaced by a short reflection of what the student said (or nothing).
TOPIC_REPLIES = {
    "exam": [
        [
            "Exams can make everything feel urgent at once.{d} Which subject or chapter is pressing on you the most right now?",
            "That pressure before tests is so real.{d} How much time do you have, and what feels the most unfinished?",
            "Studying under pressure is exhausting.{d} What's the one thing you're most worried about?",
        ],
        [
            "Let's shrink it down: pick just ONE chapter and give it 25 focused minutes, then a 5 minute break. Which one would you start with?",
            "A small plan usually feels lighter than the whole mountain. Want to dump your topics into Brain Dump so we can sort what's urgent first?",
            "You're already doing the hard part by facing it. What's one small thing you could finish in the next 30 minutes?",
        ],
        [
            "You've been carrying a lot of exam worry. Your marks don't define you. Would a short breathing reset help before you study again?",
            "It sounds like the exam pressure is really sticking. A tiny break and some water can help your brain more than another hour of panic-studying.",
        ],
    ],
    "sleep": [
        [
            "Feeling drained makes everything else feel ten times harder.{d} Have you been able to rest properly lately?",
            "That sounds exhausting.{d} What's been keeping you up or taking your energy?",
        ],
        [
            "A gentle wind-down can help: screens off 30 minutes before bed, dim lights, and a few slow breaths. Which of those feels doable tonight?",
            "Your body might be asking for rest more than for more effort. Is it hard to fall asleep, or hard to stay asleep?",
        ],
        [
            "Ongoing tiredness is worth taking seriously. If it keeps up, mention it to a parent or your school counsellor so they can help you find a routine that works.",
            "Sleep trouble is common with stress, but you deserve proper rest. Would a short body-scan reset in Quick Reset help tonight?",
        ],
    ],
    "friends": [
        [
            "Friend stuff can sit heavily on your mind all day.{d} Do you want to tell me what happened?",
            "Social stress is genuinely draining.{d} Was this sudden, or has it been building for a while?",
        ],
        [
            "That sounds really hard to navigate. How would you like things to feel between you two ideally?",
            "It makes sense that this hurts. Sometimes writing down what you'd want to say can help before talking to them. Want to try that?",
        ],
        [
            "Friendship worries can feel huge. Talking to a counsellor or someone you trust can help you see the situation from a different angle.",
            "You're handling a lot socially. Would you like a calm activity first, or keep talking it through?",
        ],
    ],
    "family": [
        [
            "Things at home can weigh on us more than anything else.{d} Do you want to tell me what's been happening?",
            "I hear you.{d} How have you been feeling about it?",
        ],
        [
            "That sounds tough. It's okay to feel mixed emotions about people you love. What do you wish they understood?",
            "Thank you for trusting me with that. Is there a calm moment when you could share how you feel with them?",
        ],
        [
            "Family pressure can feel heavy. A school counsellor can help you find words to explain how you feel at home.",
            "You're carrying a lot. Would it help to write what you'd like to say in Brain Dump first?",
        ],
    ],
    "lonely": [
        [
            "I'm really glad you told me.{d} Feeling alone is painful. How long has it felt this way?",
            "That sounds heavy. You're not alone right now, I'm here. What does lonely feel like for you today?",
        ],
        [
            "Even one small connection can help. Is there one person you'd feel okay sending a simple 'hey' to?",
            "You could also peek at MindMate Circle to see other students sharing similar feelings. Sometimes that helps.",
        ],
        [
            "Feeling lonely for a while deserves real support. A counsellor or a trusted adult can help you build connection in a way I can't.",
            "You matter, and you deserve people who show up for you. Who is one person you trust a little?",
        ],
    ],
    "sad": [
        [
            "I'm sorry you're feeling down.{d} You don't have to carry it alone. What's making today feel heavy?",
            "It's okay to feel like this sometimes.{d} Do you want to talk it through?",
        ],
        [
            "Thank you for sharing that. Is it more like something happened, or a heavy feeling with no clear reason?",
            "Being gentle with yourself matters right now. What's one tiny thing that usually brings you a bit of comfort?",
        ],
        [
            "You've been feeling low for a bit. Talking to a counsellor or someone you trust can really help you understand what's behind it.",
            "I'm here with you. Would a calm Quick Reset or some soft music help for a few minutes?",
        ],
    ],
    "anxious": [
        [
            "That sounds really uncomfortable.{d} Is the worry about something specific, or does it feel like a general knot?",
            "Anxiety can feel so loud.{d} Where do you feel it most in your body right now?",
        ],
        [
            "Let's try slowing things down together: breathe in for 4, hold for 2, out for 6. Want to try it, and then tell me how it felt?",
            "Worries often shrink when we name them. What's the very first worry that pops up?",
        ],
        [
            "You've carried this worry for a while. A counsellor can teach you tools that fit your situation. Would you consider speaking to one?",
            "You're doing well by talking about it. Would you like a grounding exercise from Quick Reset?",
        ],
    ],
    "overwhelmed": [
        [
            "When everything hits at once, it's easy to feel overwhelmed.{d} What's the number one thing weighing on you right now?",
            "That sounds like a lot at one time.{d} If you could take just one thing off your plate today, what would it be?",
        ],
        [
            "Let's make it smaller: name three things, then circle only the ONE that matters most today. Want to do that in Brain Dump?",
            "Take a slow breath with me. We can tackle things one by one. What feels like the first small step?",
        ],
        [
            "You've been under a lot of pressure. It might really help to talk to your school counsellor or a trusted adult about how much is on your plate.",
            "It's okay to ask for help with a heavy load. Who could share some of this with you?",
        ],
    ],
    "anger": [
        [
            "That sounds really frustrating.{d} What happened?",
            "Anger often shows up when something important feels unfair.{d} Do you want to vent about it?",
        ],
        [
            "It's okay to be upset. Let's let the feeling cool a little: a few slow breaths or a quick walk can help. What do you need most right now?",
            "I'm listening. What would feel like a fair outcome for you here?",
        ],
        [
            "Big feelings are easier with support. A counsellor can help you work through what's behind the frustration.",
            "You're handling a lot. Want to let it out in Brain Dump so it's out of your head?",
        ],
    ],
    "motivation": [
        [
            "Struggling to get started is so common.{d} What feels like the hardest part, the beginning or staying focused?",
            "Low motivation usually means we're tired or overloaded, not lazy.{d} What's been taking your energy?",
        ],
        [
            "Try the 5-minute trick: tell yourself you'll work for just 5 minutes. Starting is the hardest part. What's one task you could try it on?",
            "Small wins build momentum. What's the tiniest version of the task you could finish today?",
        ],
        [
            "If motivation has been low for a long time, it can be a sign you need rest or support. A counsellor can help figure out why.",
            "Let's make a mini-plan. Would you like to use Brain Dump to sort your tasks?",
        ],
    ],
    "selfesteem": [
        [
            "I'm sorry you're being so hard on yourself.{d} What made you feel that way today?",
            "That sounds painful to carry.{d} Would you say that to a friend in your position?",
        ],
        [
            "You are more than your marks or mistakes. What's one thing you did recently, however small, that you're proud of?",
            "Comparison can be harsh. What's something about you that you wouldn't trade?",
        ],
        [
            "Negative thoughts about yourself deserve real support. Please consider talking to a counsellor or a trusted adult about how you feel.",
            "You deserve kindness, including from yourself. Want to try a 'three good things' reset?",
        ],
    ],
    "phone": [
        [
            "Phones can eat up so much time, and it's hard to stop!{d} How do you feel after you scroll for a long while?",
        ],
        [
            "Try putting the phone in another room for one 25-minute study block. Does that feel doable?",
        ],
        [
            "Small, steady changes work best. Maybe pick one app to limit this week?",
        ],
    ],
}

GENERAL_REPLIES = [
    "Thanks for sharing that with me.{d} How are you feeling about it right now?",
    "I'm listening.{d} What part of this feels like it's weighing on you the most?",
    "That sounds like a lot to hold.{d} What do you think would help you feel even a little lighter today?",
    "I hear you.{d} Would you like to tell me more about what happened?",
    "I'm glad you said it out loud.{d} What's been the hardest bit?",
]

JOKES = [
    "Why did the student eat their homework? Because the teacher said it was a piece of cake! 🍰",
    "What do you call a sleeping dinosaur? A dino-snore! 🦕",
    "Why was the math book sad? It had too many problems. 📘",
    "What did the ocean say to the beach? Nothing, it just waved! 🌊",
    "Why did the sapling do so well in class? It had strong roots in the basics! 🌱",
    "Why don't scientists trust atoms? Because they make up everything! ⚛️",
]

ENCOURAGEMENTS = [
    "You showed up today, and that already takes strength.",
    "You're doing better than you think. Small steps still count.",
    "Your effort matters more than being perfect.",
    "It's okay to rest. Rest is part of doing well.",
    "You've gotten through hard days before, and you can get through this one too.",
]

POSITIVE_EMOJIS = ["😊", "😄", "🌟", "💚", "✨", "🙂"]
SOFT_EMOJIS = ["🌿", "🙂", "💚", "🤗"]
GENTLE_EMOJIS = ["🤍", "🌿"]


def _word_match(text, word):
    base = re.escape(word.rstrip("*"))
    pattern = r"\b" + base + (r"\w*" if word.endswith("*") else r"\b")
    return re.search(pattern, text) is not None


def _any_match(text, words):
    return any(_word_match(text, w) for w in words)


def detect_severity(text):
    if any(p in text for p in SEVERE_PHRASES):
        return "severe"
    if any(p in text for p in HIGH_PHRASES):
        return "high"
    if _any_match(text, STRESS_WORDS):
        return "moderate"
    return "none"


def detect_topics(text):
    scored = []
    for topic, words in TOPIC_KEYWORDS.items():
        hits = sum(1 for w in words if _word_match(text, w))
        if hits:
            scored.append((hits, topic))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [t for _, t in scored]


_PRONOUNS = {
    "i": "you", "i'm": "you're", "im": "you're", "my": "your", "me": "you", "myself": "yourself",
    "i've": "you've", "i'll": "you'll", "am": "are", "mine": "yours", "i'd": "you'd",
}


def extract_detail(text):
    match = re.search(r"\b(?:about|because of|because|with|over)\s+([a-z0-9' ]{3,40})", text)
    if not match:
        return ""
    chunk = re.split(r"\b(?:and|but|so|then|though|since)\b|[,.;!?]", match.group(1))[0].strip()
    words = chunk.split()
    if not words or words[0] in {"it", "this", "that", "them", "him", "her", "what", "how", "everything",
                                 "i", "i'm", "im", "i've", "i'll", "i'd", "we", "they", "he", "she", "you"}:
        return ""
    words = words[:6]
    flipped = " ".join(_PRONOUNS.get(w, w) for w in words)
    return flipped


def _pick(options, recent):
    def used(option):
        head = option.split("{d}")[0][:25]
        return any(head in r for r in recent)
    fresh = [o for o in options if not used(o)]
    return random.choice(fresh or options)


def _recent_assistant_texts(limit=6):
    texts = [m.get("content", "") for m in st.session_state.messages if m.get("role") == "assistant"]
    return texts[-limit:]


def first_name():
    full = (st.session_state.student_name or "").strip()
    return full.split()[0].title() if full else ""


def add_emoji(text, severity, positive=False):
    if re.search(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", text):
        return text
    if severity in ("severe", "high"):
        return f"{text} {random.choice(GENTLE_EMOJIS)}"
    if positive or severity == "none":
        return f"{text} {random.choice(POSITIVE_EMOJIS)}"
    return f"{text} {random.choice(SOFT_EMOJIS)}"


def pick_resources(topic, ctx):
    info = RESOURCE_MAP.get(topic)
    if not info:
        return []
    try:
        details = get_resource_details(info["key"])
    except Exception:
        return []
    picked = []
    start_map = info.get("start", {})
    for kind, plural in (("article", "articles"), ("video", "videos")):
        items = list(details.get(plural, []))
        offset = start_map.get(kind, 0)
        if items and 0 < offset < len(items):
            items = items[offset:] + items[:offset]
        for item in items:
            if item.get("url") and item["url"] not in ctx["shown_resources"]:
                picked.append({"kind": kind, "lead": info[kind], "title": item["title"], "url": item["url"]})
                ctx["shown_resources"].append(item["url"])
                break
    return picked[:2]


def llm_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("MINDMATE_API_KEY")
    if not key:
        try:
            key = st.secrets.get("ANTHROPIC_API_KEY")
        except Exception:
            key = None
    return key


LLM_SYSTEM_PROMPT = (
    "You are Mino, a warm, gentle companion inside MindMate, a wellbeing app for school students. "
    "Reply in 2 to 4 short sentences, in simple friendly language, responding to what the student actually said. "
    "Reflect their feeling, then ask at most one gentle question. Use one fitting emoji (a smile is fine when the "
    "mood is light, use a soft heart or leaf when they are struggling). Do not diagnose, do not give medical advice, "
    "and never describe methods of self-harm. If the student sounds very stressed or overwhelmed, kindly encourage "
    "them to talk to a school counsellor or a trusted adult. You are an AI, not a counsellor."
)


def llm_reply():
    key = llm_api_key()
    if not key:
        return None
    try:
        import urllib.request
        history = []
        for m in st.session_state.messages[-10:]:
            role = "user" if m.get("role") == "user" else "assistant"
            content = str(m.get("content", "")).strip()
            if not content:
                continue
            if history and history[-1]["role"] == role:
                history[-1]["content"] += "\n" + content
            else:
                history.append({"role": role, "content": content})
        while history and history[0]["role"] != "user":
            history.pop(0)
        if not history or history[-1]["role"] != "user":
            return None
        body = {
            "model": os.environ.get("MINDMATE_MODEL", "claude-sonnet-5-5"),
            "max_tokens": 300,
            "system": LLM_SYSTEM_PROMPT,
            "messages": history,
        }
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(body).encode("utf-8"),
            headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
        return text or None
    except Exception:
        return None


def build_smart_reply(message):
    ctx = st.session_state.chat_ctx
    ctx["turns"] += 1
    turn = ctx["turns"]
    text = message.lower().strip()
    name = first_name()
    recent = _recent_assistant_texts()
    out = {"text": "", "resources": [], "support": None, "severity": "none", "topic": None}

    # 0. "just talk" preference
    if any(k in text for k in ["don't suggest", "dont suggest", "no activity", "no activities", "just talk", "stop suggesting"]):
        st.session_state.suppress_activities = True
        out["text"] = add_emoji("Got it! No activities or exercises. I'm right here to just listen and talk. What's on your mind?", "none")
        return out

    # 1. Severe distress: calm, direct, human support first
    severity = detect_severity(text)
    out["severity"] = severity
    if severity == "severe":
        st.session_state.severe_flag_ts = time.time()
        ctx["distress_hits"] += 3
        ctx["last_support_turn"] = turn
        opener = f"{name}, " if name else ""
        out["text"] = (
            f"{opener}thank you for telling me. I'm really sorry you're hurting this much, and I'm taking what you said seriously. "
            "You deserve support from a real person right now. Please reach out to a trusted adult, your school counsellor, "
            "or a helpline below, and try not to be alone. If you might act on these thoughts or are in immediate danger, "
            "call 112 now or ask someone nearby to stay with you. I'm still here to talk, but please let a person help too. 🤍"
        )
        out["support"] = "crisis"
        return out

    topics = detect_topics(text)
    words = re.findall(r"[a-z']+", text)
    positive_words = ["happy", "good", "great", "amazing", "excited", "proud", "passed", "better", "awesome",
                      "fine", "wonderful", "glad", "relieved", "grateful", "thankful", "like", "love", "enjoy*", "fun"]
    negated = re.search(r"\b(not|no|never|can't|cant|don't|dont|didn't|didnt|won't|wasn't|isn't|nothing|hardly)\b", text) is not None
    is_positive = _any_match(text, positive_words) and severity == "none" and not negated
    awaiting = ctx.get("awaiting")
    reply = None

    # 2. Short yes/no follow-ups to what Mino just asked
    short_yes = text in {"yes", "yeah", "yep", "sure", "ok sure", "okay sure", "please", "yes please", "ya", "yup"}
    short_no = text in {"no", "nope", "nah", "no thanks", "not really", "no thank you"}
    if awaiting and not (short_yes or short_no):
        ctx["awaiting"] = None
        awaiting = None
    if awaiting == "joke" and (short_yes or short_no):
        ctx["awaiting"] = None
        if short_yes:
            reply = random.choice(JOKES) + " Want to tell me how your day has actually been?"
        else:
            reply = "No worries at all 🌿 I'm here whenever you want to talk about anything."
    elif (short_yes or short_no) and ctx.get("last_topic"):
        reply = ("Okay, tell me more. What part feels the hardest?" if short_yes
                 else "That's okay. We can go at your pace. Do you want to talk about something else, or just sit with it for a moment?")
    elif _any_match(text, ["joke", "funny", "make me laugh", "laugh"]):
        reply = random.choice(JOKES)
    elif _any_match(text, ["cheer me up", "motivate me", "compliment me", "encourage me", "motivation quote"]):
        reply = random.choice(ENCOURAGEMENTS) + " What's one thing you're proud of lately?"
    elif _any_match(text, ["who are you", "what are you", "are you real", "are you a bot", "are you human", "your name"]):
        reply = ("I'm Mino, MindMate's friendly companion 🌿 I'm an AI, not a person or a counsellor. "
                 "I can listen, share calming tools, and point you to real people when you need them.")
    elif _any_match(text, ["counsellor", "counselor", "trusted adult", "talk to someone", "need help", "need someone"]):
        reply = ("Reaching out is a brave and wise step. A counsellor or trusted adult can understand your personal situation "
                 "in ways I can't. You can see their details below.")
        out["support"] = "nudge"
        ctx["last_support_turn"] = turn
    elif _any_match(text, ["article*", "video*", "resource*", "read something", "watch something", "book*"]):
        reply = "Happy to share some! Here are a couple of picks that might help you."
    elif _any_match(text, ["thank*", "thx", "appreciate"]):
        reply = random.choice([
            "You're so welcome! I'm glad it helped.",
            "Anytime! I'm always happy to listen.",
        ])
    elif _any_match(text, ["bye", "goodbye", "good night", "see you", "gtg", "talk later"]):
        reply = random.choice([
            "Take care of yourself! Come back anytime you want to talk 🌿",
            "Bye for now! Be kind to yourself today 😊",
        ])
    elif words and len(words) <= 6 and _any_match(text, ["hi", "hello", "hey", "hii", "heyy", "sup", "yo", "namaste"]) and not topics:
        who = f", {name}" if name else ""
        reply = random.choice([
            f"Hey{who}! I'm Mino 🌿 How are you feeling today?",
            f"Hello{who}! Glad you stopped by. What's on your mind?",
            f"Hi{who}! I'm right here with you. How has your day been so far?",
        ])
    elif is_positive:
        reply = random.choice([
            "That's lovely to hear! What made today feel good?",
            "Yay, I'm happy for you! What's been the best part?",
            "That's great! Celebrate the little wins. What helped you feel this way?",
        ])
    elif _any_match(text, ["what should i do", "what do i do", "any advice", "any suggestions", "help me", "how do i"]):
        topic = ctx.get("last_topic") or (topics[0] if topics else None)
        if topic in TOPIC_REPLIES:
            stage_list = TOPIC_REPLIES[topic][1] if len(TOPIC_REPLIES[topic]) > 1 else TOPIC_REPLIES[topic][0]
            reply = _pick([r.replace("{d}", "") for r in stage_list], recent)
            out["topic"] = topic
        else:
            reply = "I'd love to help. Can you tell me a bit more about what's going on, so I can suggest something that fits?"

    # 3. Topic-based, stage-aware reply
    if reply is None:
        primary = topics[0] if topics else None
        if primary and primary in TOPIC_REPLIES:
            count = ctx["topic_counts"].get(primary, 0)
            stage = min(count, len(TOPIC_REPLIES[primary]) - 1)
            detail = extract_detail(text)
            d_line = f" Thinking about {detail} sounds heavy." if detail else ""
            template = _pick(TOPIC_REPLIES[primary][stage], recent)
            reply = template.replace("{d}", d_line)
            ctx["topic_counts"][primary] = count + 1
            ctx["last_topic"] = primary
            out["topic"] = primary
        else:
            detail = extract_detail(text)
            d_line = f" Thinking about {detail} sounds like a lot." if detail else ""
            reply = _pick(GENERAL_REPLIES, recent).replace("{d}", d_line)

    # 4. Distress accounting and human-support nudge
    if severity == "high":
        ctx["distress_hits"] += 2
    elif severity == "moderate" or any(t in DISTRESS_TOPICS for t in topics):
        ctx["distress_hits"] += 1
    needs_nudge = (
        (severity == "high" and turn - ctx["last_support_turn"] >= 2)
        or (ctx["distress_hits"] >= 3 and turn - ctx["last_support_turn"] >= 5)
    )
    if needs_nudge and out["support"] is None:
        out["support"] = "nudge"
        ctx["last_support_turn"] = turn
        reply += (
            "\n\nIf this feels like too much to carry, please think about talking to your school counsellor or a trusted adult. "
            "A real person can understand your individual situation and support you in ways I can't."
        )

    # 5. Resource suggestions (only when it fits and not too often)
    topic_for_res = out["topic"] or ctx.get("last_topic")
    asked_resources = _any_match(text, ["article*", "video*", "resource*", "read something", "watch something", "book*"])
    stage_now = ctx["topic_counts"].get(topic_for_res, 0) if topic_for_res else 0
    wants_resources = asked_resources or (
        not st.session_state.suppress_activities
        and turn - ctx["last_resource_turn"] >= 3
        and (stage_now >= 2 or severity in ("moderate", "high"))
    )
    if wants_resources:
        picks = pick_resources(topic_for_res, ctx) if topic_for_res in RESOURCE_MAP else []
        if not picks and asked_resources:
            picks = pick_resources("overwhelmed", ctx)
        if picks:
            out["resources"] = picks
            ctx["last_resource_turn"] = turn

    # 6. Light, positive touch (only when the mood is light enough)
    if (
        severity == "none"
        and not out["support"]
        and ctx["distress_hits"] == 0
        and out["topic"] in (None, "phone", "motivation")
        and turn >= 3
        and turn - ctx["last_light_turn"] >= 6
        and not st.session_state.suppress_activities
        and ctx.get("awaiting") is None
    ):
        reply += "\n\nBy the way, want a tiny joke to lighten the mood? 😄"
        ctx["awaiting"] = "joke"
        ctx["last_light_turn"] = turn

    # 7. Optional natural-language model (only if an API key is configured)
    smart_text = llm_reply()
    if smart_text:
        reply = smart_text
        ctx["awaiting"] = None
        if out["support"] == "nudge" and severity == "high":
            reply += (
                "\n\nPlease think about talking to your school counsellor or a trusted adult. "
                "A real person can understand your individual situation and support you in ways I can't."
            )

    out["text"] = add_emoji(reply, severity, positive=is_positive)
    return out


# ------------------------------------------------------------
# 4f. SUPPORT PANEL, CHAT LIMITS AND LOCKS
# ------------------------------------------------------------

CHAT_SOFT_REMINDER_SECONDS = 45 * 60      # gentle break reminder
CHAT_HARD_LIMIT_SECONDS = 90 * 60         # positive close + temporary lock
CHAT_LOCK_SECONDS = 10 * 60 * 60          # 10 hours
CHAT_BREAK_RESET_SECONDS = 10 * 60        # a 10 minute pause counts as a real break
CHAT_ACCESS_LIMIT = 5                     # more than 5 openings...
CHAT_ACCESS_WINDOW_SECONDS = 2 * 60 * 60  # ...within 2 hours
CHAT_ACCESS_LOCK_SECONDS = 30 * 60        # 30 minute breather
IDLE_LOCK_SECONDS = 15 * 60               # app lock after 15 minutes idle

LIMITS_FILE = DATA_DIR / "chat_limits.json"


def render_support_panel(key_prefix, urgent=False):
    with st.container():
        st.markdown("### 🤍 Please reach out to a real person" if urgent else "### 🤝 Human support can help")
        st.write(
            "A school counsellor or trusted adult can understand your individual situation and support you in ways an app cannot."
        )
        adult = st.session_state.trusted_adult_info
        if adult:
            contact = str(adult.get("Contact", ""))
            digits = re.sub(r"[^\d+]", "", contact)
            st.markdown(
                f"**{escape(str(adult.get('Name', 'Trusted adult')))}** ({escape(str(adult.get('Relationship', 'Support')))}): "
                f"[📞 {escape(contact)}](tel:{digits})"
            )
        else:
            st.caption("You haven't added a trusted adult yet. You can add one in your Profile.")
            st.button("Add a trusted adult", key=f"{key_prefix}_profile", on_click=go_to, args=("Profile",), use_container_width=True)
        st.markdown("• **Childline Support:** Call `1098` (free, 24/7)")
        st.markdown("• **Mental Health Helpline:** Call `14416` or `1800-891-4416`")
        st.markdown("• **Immediate danger:** Call `112`")
        st.markdown("• [Find student counsellors nearby 🔗](https://www.google.com/maps/search/student+counsellors+near+me/)")


def render_message_extras(message, index):
    for res in message.get("resources") or []:
        icon = "📄" if res.get("kind") == "article" else "🎬"
        st.markdown(
            f'<div class="step-item-card">{escape(res.get("lead", ""))}:<br>'
            f'{icon} <a href="{escape(res.get("url", ""))}" target="_blank">{escape(res.get("title", ""))}</a></div>',
            unsafe_allow_html=True,
        )
    support = message.get("support")
    if support == "crisis":
        render_support_panel(f"crisis_{index}", urgent=True)
    elif support == "nudge":
        render_support_panel(f"nudge_{index}", urgent=False)


def limits_user_key():
    n = (st.session_state.student_name or "").strip().lower()
    c = (st.session_state.student_class or "").strip().lower()
    return f"{n}|{c}" if (n or c) else str(st.session_state.student_id)


def limits_read():
    try:
        if LIMITS_FILE.exists():
            return json.loads(LIMITS_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def limits_write(data):
    try:
        LIMITS_FILE.write_text(json.dumps(data), encoding="utf-8")
    except Exception:
        pass


def chat_lock_status():
    rec = limits_read().get(limits_user_key(), {})
    until = float(rec.get("locked_until", 0) or 0)
    now = time.time()
    if until > now:
        return True, until - now, rec.get("lock_reason", "")
    return False, 0, ""


def chat_set_lock(seconds, reason):
    data = limits_read()
    rec = data.setdefault(limits_user_key(), {})
    rec["locked_until"] = time.time() + seconds
    rec["lock_reason"] = reason
    limits_write(data)


def chat_register_access():
    data = limits_read()
    rec = data.setdefault(limits_user_key(), {})
    now = time.time()
    times = [t for t in rec.get("access_times", []) if now - t < CHAT_ACCESS_WINDOW_SECONDS]
    times.append(now)
    rec["access_times"] = times
    flagged = st.session_state.severe_flag_ts
    exempt = bool(flagged and now - flagged < CHAT_ACCESS_WINDOW_SECONDS)
    already_locked = float(rec.get("locked_until", 0) or 0) > now
    if len(times) > CHAT_ACCESS_LIMIT and not exempt and not already_locked:
        rec["locked_until"] = now + CHAT_ACCESS_LOCK_SECONDS
        rec["lock_reason"] = "frequent"
        rec["access_times"] = []
    limits_write(data)


def chat_track_activity():
    now = time.time()
    last = st.session_state.chat_last_msg_ts
    if last is None or now - last > CHAT_BREAK_RESET_SECONDS:
        st.session_state.chat_session_start = now
        st.session_state.chat_reminder_shown = False
    st.session_state.chat_last_msg_ts = now


def chat_check_time_limits():
    now = time.time()
    start = st.session_state.chat_session_start or now
    elapsed = now - start
    if elapsed >= CHAT_HARD_LIMIT_SECONDS:
        st.session_state.messages.append({
            "role": "assistant",
            "kind": "conclusion",
            "content": (
                "We've been chatting for a long while, and I'm really proud of you for taking this time for yourself 🌟 "
                "Let's pause our chat now so you can rest, drink some water and do something you enjoy. "
                "Chat will open again in 10 hours. You did great today! 💚"
            ),
        })
        chat_set_lock(CHAT_LOCK_SECONDS, "duration")
        st.session_state.chat_session_start = None
        st.session_state.chat_last_msg_ts = None
        st.session_state.chat_reminder_shown = False
    elif elapsed >= CHAT_SOFT_REMINDER_SECONDS and not st.session_state.chat_reminder_shown:
        st.session_state.chat_reminder_shown = True
        st.session_state.messages.append({
            "role": "assistant",
            "kind": "break_reminder",
            "content": (
                "Gentle reminder: we've been chatting for about 45 minutes. 🌿 This might be a good moment to stretch, "
                "sip some water or rest your eyes for a few minutes. I'll be right here when you're ready 😊"
            ),
        })


def go_games():
    st.session_state.explore_tab = "games"
    st.session_state.page = "Explore"


def render_chat_lock_screen(remaining, reason):
    hrs, rest = divmod(int(remaining), 3600)
    mins = max(1, rest // 60) if hrs == 0 else rest // 60
    time_txt = f"{hrs}h {mins}m" if hrs else f"{mins} min"
    if reason == "frequent":
        title = "🌿 Let's take a little breather"
        body = (
            "You've opened the chat quite a few times in a short while. That's okay, and it's a good sign that you want support. "
            "Let's give your mind a small break so you can reset. The chat will reopen soon."
        )
    else:
        title = "🌟 Great chatting today!"
        body = (
            "You spent a lot of time looking after yourself today, and that's something to be proud of. "
            "Chat is resting for a while so you can recharge. You did really well, and I'll be here when you're back. 💚"
        )
    st.markdown(
        textwrap.dedent(f"""
        <div class="welcome-card">
            <div class="brand-small">CHAT IS RESTING</div>
            <div class="welcome-title">{title}</div>
            <div class="welcome-subtitle">{body}</div>
        </div>
        """),
        unsafe_allow_html=True,
    )
    st.info(f"⏳ Chat reopens in about {time_txt}.")

    st.markdown("### 💚 While you wait, you can still:")
    b1, b2, b3 = st.columns(3)
    with b1:
        st.button("🌿 Quick Reset", key="lock_go_act", on_click=go_to, args=("Activities",), use_container_width=True)
    with b2:
        st.button("🎮 Mini-Games", key="lock_go_games", on_click=go_games, use_container_width=True)
    with b3:
        st.button("🧠 Brain Dump", key="lock_go_dump", on_click=go_to, args=("Brain Dump",), use_container_width=True)

    try:
        vids = get_resource_details("Understanding Everyday Stress").get("videos", [])
        arts = get_resource_details("Understanding Everyday Stress").get("articles", [])
        if vids:
            st.markdown(f"This video might help you relax: 🎬 [{vids[1]['title'] if len(vids) > 1 else vids[0]['title']}]({(vids[1] if len(vids) > 1 else vids[0])['url']})")
        if arts:
            st.markdown(f"You could refer to this article for managing everyday stress: 📄 [{arts[0]['title']}]({arts[0]['url']})")
    except Exception:
        pass

    render_support_panel("lock", urgent=False)


# ------------------------------------------------------------
# 4g. CALMING MUSIC LIBRARY (your files + generated ambient sounds)
# ------------------------------------------------------------

AUDIO_MIME = {".mp3": "audio/mpeg", ".wav": "audio/wav", ".ogg": "audio/ogg", ".m4a": "audio/mp4"}
AMBIENT_DIR = ASSETS_DIR / "ambient"
AMBIENT_TRACKS = {
    "🌙 Soft Pads": "soft_pads",
    "🌧️ Gentle Rain": "gentle_rain",
    "🌊 Ocean Waves": "ocean_waves",
    "🔔 Singing Bowl": "singing_bowl",
}


def generate_ambient_track(kind, path, seconds=20, rate=16000):
    rnd = random.Random(11)
    total = seconds * rate
    data = array.array("h")
    two_pi = 2 * math.pi
    samples = []

    if kind == "soft_pads":
        freqs = [130.81, 164.81, 196.0, 246.94, 293.66]
        lfos = [(0.07, 0.0), (0.11, 1.3), (0.09, 2.1), (0.13, 3.0), (0.08, 4.2)]
        for i in range(total):
            t = i / rate
            v = 0.0
            for f, (lf, ph) in zip(freqs, lfos):
                v += math.sin(two_pi * f * t) * (0.55 + 0.45 * math.sin(two_pi * lf * t + ph)) * 0.17
            samples.append(v)
    elif kind == "gentle_rain":
        y1 = y2 = 0.0
        drop = 0.0
        for i in range(total):
            x = rnd.uniform(-1, 1)
            y1 += 0.35 * (x - y1)
            y2 += 0.04 * (x - y2)
            if rnd.random() < 0.0007:
                drop = rnd.uniform(0.2, 0.5)
            drop *= 0.985
            samples.append(0.55 * y1 + 1.4 * y2 + drop * rnd.uniform(-1, 1) * 0.5)
    elif kind == "ocean_waves":
        y = 0.0
        for i in range(total):
            t = i / rate
            x = rnd.uniform(-1, 1)
            y += 0.06 * (x - y)
            swell = (0.5 + 0.5 * math.sin(two_pi * t / 8.0)) ** 1.5 * 0.9 + 0.1
            samples.append(y * swell * 3.2)
    else:  # singing_bowl
        partials = [(220.0, 1.0), (220.0 * 2.756, 0.4), (220.0 * 5.404, 0.15)]
        for i in range(total):
            t = i / rate
            tm = t % 5.0
            env = math.exp(-tm / 1.6) * min(1.0, tm / 0.03)
            v = sum(a * math.sin(two_pi * f * t) for f, a in partials) * env * 0.35
            samples.append(v)

    peak = max(1e-9, max(abs(s) for s in samples))
    scale = 0.6 / peak
    fade = int(1.0 * rate)
    for i, s in enumerate(samples):
        gain = 1.0
        if i < fade:
            gain = i / fade
        elif i > total - fade:
            gain = (total - i) / fade
        data.append(int(max(-1.0, min(1.0, s * scale * gain)) * 32767))

    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(data.tobytes())


def music_options():
    options = {}
    try:
        for f in sorted(ASSETS_DIR.iterdir()):
            if f.is_file() and f.suffix.lower() in AUDIO_MIME:
                stem = f.stem.replace("-", " ").replace("_", " ").strip().title()
                label = "🎧 Soothing (original)" if f.stem.lower() == "soothing" else f"🎧 {stem[:28]}"
                options[label] = {"path": f, "mime": AUDIO_MIME[f.suffix.lower()], "kind": None}
    except Exception:
        pass
    for label, kind in AMBIENT_TRACKS.items():
        options[label] = {"path": AMBIENT_DIR / f"{kind}.wav", "mime": "audio/wav", "kind": kind}
    return options


@st.cache_data(show_spinner=False)
def read_audio_bytes(path_str, mtime):
    return Path(path_str).read_bytes()



# ============================================================
# 5. DYNAMIC CSS & MASCOT STYLING
# ============================================================

theme = st.session_state.theme_mode

if theme == "light":
    css_vars = """
        --bg-warm: #FAF8F5;
        --card-warm: #FFFFFF;
        --card-soft: #F6F2EC;
        --accent-sage: #6E8B74;
        --accent-sage-light: #EBF1EC;
        --accent-terracotta: #E08E79;
        --text-dark: #2C3531;
        --text-muted: #6B7B73;
        --border-soft: #EAE5DE;
        --input-bg: #FFFFFF;
        --chat-user-bg: #E2ECE5;
        --tab-bg: #EFEAE4;
        --tab-active-bg: #6E8B74;
        --tab-active-text: #FFFFFF;
        --link-color: #3E6B52;
        --alert-warn-bg: #FBF1D9;
        --alert-err-bg: #FBE4DE;
    """
else:
    css_vars = """
        --bg-warm: #121816;
        --card-warm: #1A2320;
        --card-soft: #222C28;
        --accent-sage: #8EAFA0;
        --accent-sage-light: #25332C;
        --accent-terracotta: #F0A089;
        --text-dark: #ECEFED;
        --text-muted: #9BB0A5;
        --border-soft: #2D3A34;
        --input-bg: #222C28;
        --chat-user-bg: #2B4036;
        --tab-bg: #222C28;
        --tab-active-bg: #8EAFA0;
        --tab-active-text: #121816;
        --link-color: #A9D1BC;
        --alert-warn-bg: #3A3322;
        --alert-err-bg: #3D2824;
    """

color_scheme = "dark" if theme == "dark" else "light"

st.markdown(
    textwrap.dedent(f"""
    <style>
    :root {{
        {css_vars}
    }}

    .stApp, .main {{
        background-color: var(--bg-warm) !important;
        transition: background-color 0.3s ease;
    }}

    .block-container {{
        max-width: 760px !important;
        padding-top: 1rem !important;
        padding-bottom: 9.5rem !important;
        margin: 0 auto !important;
    }}

    @media (min-width: 992px) {{
        .block-container {{
            max-width: 880px !important;
        }}
    }}

    body, p, span, div, label {{
        color: var(--text-dark) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}

    h1, h2, h3, h4 {{
        color: var(--text-dark) !important;
        font-weight: 700 !important;
    }}

    div[data-testid="stForm"], div[data-testid="stExpander"], div[data-testid="stContainer"] {{
        background-color: var(--card-warm);
        border: 1px solid var(--border-soft);
        border-radius: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.02);
    }}

    .stButton > button {{
        border-radius: 16px !important;
        border: 1px solid var(--border-soft) !important;
        background-color: var(--card-warm) !important;
        color: var(--text-dark) !important;
        min-height: 46px;
        font-weight: 600;
        transition: all 0.25s ease;
        padding: 6px 14px;
    }}

    .stButton > button:hover {{
        border-color: var(--accent-sage) !important;
        background-color: var(--accent-sage-light) !important;
        color: var(--accent-sage) !important;
        transform: translateY(-2px);
    }}

    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {{
        border-radius: 18px !important;
        border: 1px solid var(--border-soft) !important;
        background-color: var(--input-bg) !important;
        color: var(--text-dark) !important;
        padding: 12px 16px !important;
    }}

    .welcome-card {{
        background: linear-gradient(135deg, var(--card-soft) 0%, var(--card-warm) 100%);
        border: 1px solid var(--border-soft);
        border-radius: 24px;
        padding: 24px 20px;
        margin-bottom: 20px;
    }}

    .welcome-title {{ font-size: 26px; font-weight: 700; color: var(--text-dark); margin-bottom: 6px; }}
    .welcome-subtitle {{ font-size: 14px; line-height: 1.5; color: var(--text-muted); }}
    .brand-small {{ font-size: 11px; letter-spacing: 0.8px; color: var(--accent-terracotta); font-weight: 700; text-transform: uppercase; margin-bottom: 6px; }}

    .chat-user {{ display: flex; justify-content: flex-end; margin: 12px 0; }}
    .chat-user-bubble {{ max-width: 86%; background-color: var(--chat-user-bg); color: var(--text-dark); padding: 13px 17px; border-radius: 22px 22px 4px 22px; font-size: 15px; }}

    .chat-ai {{ display: flex; justify-content: flex-start; margin: 12px 0; }}
    .chat-ai-bubble {{ max-width: 88%; background-color: var(--card-warm); color: var(--text-dark); padding: 15px 18px; border-radius: 22px 22px 22px 4px; border: 1px solid var(--border-soft); font-size: 15px; }}
    .chat-label {{ font-size: 11px; color: var(--accent-sage); font-weight: 700; margin-bottom: 4px; }}

    /* FLOATING BOTTOM-LEFT CLICKABLE MASCOT WITH COMPACT BUBBLE */
    .fixed-mascot-container {{
        position: fixed;
        bottom: 75px;
        left: 15px;
        z-index: 999999;
        display: flex;
        align-items: flex-end;
        gap: 6px;
        pointer-events: none;
    }}

    .speech-bubble-compact {{
        background: var(--card-warm);
        border: 1px solid var(--accent-sage);
        color: var(--text-dark);
        padding: 4px 8px;
        border-radius: 10px 10px 10px 0px;
        font-size: 10px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        animation: floatBubble 3s ease-in-out infinite;
        white-space: nowrap;
    }}

    .character-avatar-compact {{
        width: 48px;
        height: 48px;
        background: #8CCFA9;
        border: 2px solid #70B995;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        animation: floatMascot 2.5s ease-in-out infinite;
    }}

    @keyframes floatMascot {{
        0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
        50% {{ transform: translateY(-6px) rotate(3deg); }}
    }}

    @keyframes floatBubble {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-2px); }}
    }}

    /* OVERLAY CLICK AREA FOR MASCOT */
    div[data-testid="stButton"] button[key="floating_mascot_chat_trigger"] {{
        position: fixed !important;
        bottom: 75px !important;
        left: 15px !important;
        width: 210px !important;
        height: 55px !important;
        z-index: 9999999 !important;
        opacity: 0 !important;
        cursor: pointer !important;
    }}

    .completion-banner {{
        background: linear-gradient(135deg, #6E8B74 0%, #E08E79 100%);
        color: white !important;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        font-size: 20px;
        font-weight: 800;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        margin: 16px 0;
    }}

    .mood-note {{ background-color: var(--card-soft); border-radius: 16px; padding: 12px 16px; margin: 10px 0; font-size: 14px; font-weight: 500; }}
    .step-item-card {{ background-color: var(--card-soft) !important; border-left: 4px solid var(--accent-sage) !important; padding: 12px 16px !important; border-radius: 10px !important; margin: 8px 0 !important; font-size: 14px !important; }}

    .calendar-table {{ width: 100%; border-collapse: collapse; text-align: center; margin-top: 10px; }}
    .calendar-table th {{ font-size: 12px; color: var(--accent-sage); padding: 8px 0; font-weight: 700; }}
    .calendar-table td {{ width: 14%; height: 50px; border: 1px solid var(--border-soft); border-radius: 10px; font-size: 12px; vertical-align: top; padding: 4px; background-color: var(--card-warm); }}

    .game-badge {{
        background: linear-gradient(135deg, var(--accent-sage) 0%, #56725C 100%);
        color: white !important;
        padding: 6px 14px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 10px;
    }}

    /* ===================== LIGHT / DARK COMPATIBILITY ===================== */
    /* Streamlit's own widgets follow the browser/OS theme, so everything below forces them
       to follow MindMate's Light/Dark toggle instead. */
    :root {{ color-scheme: {color_scheme}; }}

    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
        background-color: var(--bg-warm) !important;
        color: var(--text-dark) !important;
    }}
    header[data-testid="stHeader"] {{ background-color: var(--bg-warm) !important; }}
    header[data-testid="stHeader"] *, [data-testid="stToolbar"] * {{ color: var(--text-dark) !important; }}

    a, a:visited, .stMarkdown a {{ color: var(--link-color) !important; }}
    a:hover {{ color: var(--accent-terracotta) !important; }}

    code, pre, [data-testid="stCode"], [data-testid="stCode"] pre {{
        background-color: var(--accent-sage-light) !important;
        color: var(--text-dark) !important;
    }}
    code {{ border-radius: 6px; padding: 1px 6px; }}
    pre code {{ background: transparent !important; padding: 0; }}
    code *, pre * {{ color: var(--text-dark) !important; }}

    hr {{ border-color: var(--border-soft) !important; }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{ border-color: var(--border-soft) !important; }}

    input::placeholder, textarea::placeholder {{ color: var(--text-muted) !important; opacity: 0.85 !important; }}
    div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"] {{
        background-color: var(--input-bg) !important;
        border-color: var(--border-soft) !important;
        border-radius: 18px !important;
    }}

    /* dropdowns (selectbox) and their open menu */
    div[data-baseweb="select"] > div {{
        background-color: var(--input-bg) !important;
        border-color: var(--border-soft) !important;
        border-radius: 16px !important;
    }}
    div[data-baseweb="select"] div, div[data-baseweb="select"] span, div[data-baseweb="select"] input {{
        color: var(--text-dark) !important;
        -webkit-text-fill-color: var(--text-dark) !important;
    }}
    div[data-baseweb="select"] svg {{ fill: var(--text-muted) !important; color: var(--text-muted) !important; }}
    div[data-baseweb="popover"] > div, div[data-baseweb="menu"], ul[role="listbox"] {{
        background-color: var(--card-warm) !important;
        border: 1px solid var(--border-soft) !important;
        border-radius: 14px !important;
    }}
    ul[role="listbox"] li, li[role="option"] {{ background-color: var(--card-warm) !important; color: var(--text-dark) !important; }}
    ul[role="listbox"] li *, li[role="option"] * {{ color: var(--text-dark) !important; }}
    ul[role="listbox"] li:hover, li[role="option"]:hover, li[role="option"][aria-selected="true"] {{
        background-color: var(--accent-sage-light) !important;
    }}

    /* popover (the 🎵 Music menu) */
    div[data-testid="stPopover"] > button, button[data-testid="stPopoverButton"] {{
        border-radius: 16px !important;
        border: 1px solid var(--border-soft) !important;
        background-color: var(--card-warm) !important;
        color: var(--text-dark) !important;
        min-height: 46px;
        font-weight: 600;
    }}
    div[data-testid="stPopover"] > button:hover, button[data-testid="stPopoverButton"]:hover {{
        border-color: var(--accent-sage) !important;
        background-color: var(--accent-sage-light) !important;
    }}
    div[data-testid="stPopoverBody"] {{
        background-color: var(--card-warm) !important;
        border: 1px solid var(--border-soft) !important;
        border-radius: 18px !important;
    }}

    /* form submit + download buttons (not covered by .stButton) */
    div[data-testid="stFormSubmitButton"] > button, .stDownloadButton > button {{
        border-radius: 16px !important;
        border: 1px solid var(--border-soft) !important;
        background-color: var(--card-warm) !important;
        color: var(--text-dark) !important;
        min-height: 46px;
        font-weight: 600;
    }}
    div[data-testid="stFormSubmitButton"] > button:hover, .stDownloadButton > button:hover {{
        border-color: var(--accent-sage) !important;
        background-color: var(--accent-sage-light) !important;
    }}

    /* info / success / warning / error boxes */
    div[data-testid="stAlert"], div[data-testid="stAlertContainer"] {{
        background-color: var(--accent-sage-light) !important;
        border-radius: 16px !important;
    }}
    div[data-testid="stAlertContainer"], div[data-testid="stAlert"]:not(:has(div[data-testid="stAlertContainer"])) {{
        border: 1px solid var(--border-soft) !important;
    }}
    div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]),
    div[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {{ background-color: var(--alert-warn-bg) !important; }}
    div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]),
    div[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {{ background-color: var(--alert-err-bg) !important; }}
    div[data-testid="stAlert"] *, div[data-testid="stAlertContainer"] * {{ color: var(--text-dark) !important; }}

    /* expanders (games, saved records, helplines) */
    div[data-testid="stExpander"] details, div[data-testid="stExpander"] summary {{
        background-color: transparent !important;
        color: var(--text-dark) !important;
        border-color: var(--border-soft) !important;
    }}
    div[data-testid="stExpander"] summary:hover {{ background-color: var(--accent-sage-light) !important; }}
    div[data-testid="stExpander"] summary svg {{ color: var(--text-muted) !important; }}

    /* sidebar + toasts */
    section[data-testid="stSidebar"] > div, [data-testid="stSidebarContent"] {{ background-color: var(--card-soft) !important; }}
    [data-testid="stSidebarCollapsedControl"] *, [data-testid="stExpandSidebarButton"] *, [data-testid="stSidebarCollapseButton"] * {{ color: var(--text-dark) !important; }}
    div[data-testid="stToast"] {{ background-color: var(--card-warm) !important; border: 1px solid var(--border-soft) !important; }}
    </style>
    """),
    unsafe_allow_html=True,
)


st.markdown(
    """
    <style>
    /* ===================== MASCOT: green sapling buddy ===================== */
    .mm-mascot-wrap {
        position: fixed; bottom: 78px; left: 10px; z-index: 999999;
        display: flex; align-items: flex-end; gap: 2px; pointer-events: none;
    }
    .mm-mascot-stage { width: 84px; height: 104px; position: relative; }
    .mm-mascot-svg {
        width: 84px; height: 104px; overflow: visible;
        transform-origin: 50% 100%;
        animation: mmDance 9s ease-in-out infinite;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.12));
    }
    .mm-cloud {
        position: relative; margin-bottom: 64px; margin-left: -2px;
        background: var(--card-warm); border: 1px solid var(--accent-sage);
        color: var(--text-dark); padding: 3px 9px; border-radius: 14px;
        font-size: 9.5px; font-weight: 700; line-height: 1.25; white-space: nowrap;
        box-shadow: 0 2px 8px rgba(0,0,0,0.10);
        animation: mmCloud 3s ease-in-out infinite;
    }
    .mm-cloud::before {
        content: ""; position: absolute; left: -6px; bottom: -4px; width: 7px; height: 7px;
        background: var(--card-warm); border: 1px solid var(--accent-sage); border-radius: 50%;
    }
    .mm-cloud::after {
        content: ""; position: absolute; left: -11px; bottom: -9px; width: 4px; height: 4px;
        background: var(--card-warm); border: 1px solid var(--accent-sage); border-radius: 50%;
    }
    @keyframes mmCloud { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-2px); } }

    @keyframes mmDance {
        0%, 100% { transform: translateY(0) rotate(0deg) scaleX(1); }
        6%  { transform: translateY(-9px) rotate(-7deg) scaleX(1); }
        12% { transform: translateY(0) rotate(7deg) scaleX(1); }
        18% { transform: translateY(-9px) rotate(-7deg) scaleX(1); }
        24% { transform: translateY(0) rotate(0deg) scaleX(1); }
        34% { transform: translateY(-5px) rotate(11deg) scaleX(1); }
        42% { transform: translateY(0) rotate(-11deg) scaleX(1); }
        50% { transform: translateY(-5px) rotate(11deg) scaleX(1); }
        58% { transform: translateY(0) rotate(0deg) scaleX(1); }
        66% { transform: translateY(-14px) rotate(0deg) scaleX(-1); }
        72% { transform: translateY(0) rotate(0deg) scaleX(-1); }
        80% { transform: translateY(-14px) rotate(0deg) scaleX(1); }
        86% { transform: translateY(0) rotate(0deg) scaleX(1); }
        93% { transform: translateY(-4px) rotate(-4deg) scaleX(1); }
    }
    .mm-armL { transform-origin: 30px 88px; animation: mmArmL 0.7s ease-in-out infinite alternate; }
    .mm-armR { transform-origin: 90px 88px; animation: mmArmR 0.7s ease-in-out infinite alternate; }
    @keyframes mmArmL { from { transform: rotate(-30deg); } to { transform: rotate(35deg); } }
    @keyframes mmArmR { from { transform: rotate(30deg); } to { transform: rotate(-35deg); } }
    .mm-legL { transform-origin: 47px 118px; animation: mmLegL 0.7s ease-in-out infinite alternate; }
    .mm-legR { transform-origin: 73px 118px; animation: mmLegR 0.7s ease-in-out infinite alternate; }
    @keyframes mmLegL { from { transform: rotate(8deg); } to { transform: rotate(-8deg); } }
    @keyframes mmLegR { from { transform: rotate(-8deg); } to { transform: rotate(8deg); } }
    .mm-leaf { transform-origin: 60px 44px; animation: mmLeaf 1.6s ease-in-out infinite alternate; }
    @keyframes mmLeaf { from { transform: rotate(-7deg); } to { transform: rotate(7deg); } }
    .mm-eyes { transform-box: fill-box; transform-origin: center; animation: mmBlink 4s infinite; }
    @keyframes mmBlink { 0%, 92%, 100% { transform: scaleY(1); } 95% { transform: scaleY(0.1); } }
    .mm-shadow { transform-origin: 60px 144px; animation: mmShadow 0.7s ease-in-out infinite alternate; }
    @keyframes mmShadow { from { transform: scaleX(1); opacity: 0.9; } to { transform: scaleX(0.85); opacity: 0.6; } }

    /* click area (invisible button laid over the mascot + cloud) */
    .st-key-floating_mascot_chat_trigger {
        position: fixed !important; bottom: 70px !important; left: 8px !important;
        width: 175px !important; height: 118px !important; z-index: 9999999 !important;
    }
    .st-key-floating_mascot_chat_trigger button {
        width: 100% !important; height: 100% !important; opacity: 0 !important; cursor: pointer !important;
    }

    /* hidden button the idle-lock watcher clicks (kept off-screen, not display:none) */
    .st-key-idle_lock_trigger {
        position: absolute !important; left: -9999px !important; top: 0 !important;
        width: 1px !important; height: 1px !important; overflow: hidden !important;
    }

    /* ===================== SIDEBAR (RECORDS) ===================== */
    section[data-testid="stSidebar"] { background-color: var(--card-soft) !important; border-right: 1px solid var(--border-soft); }
    section[data-testid="stSidebar"] .stButton > button { min-height: 36px; font-size: 13px; }

    /* ===================== MINDMATE CIRCLE ===================== */
    div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 22px !important; }
    .cp-head { display: flex; align-items: center; gap: 11px; margin-bottom: 8px; }
    .cp-avatar {
        width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-size: 22px; flex-shrink: 0; border: 2px solid var(--card-warm); box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .cp-name { font-size: 14.5px; font-weight: 700; color: var(--text-dark); }
    .cp-time { font-size: 11.5px; color: var(--text-muted) !important; font-weight: 500; }
    .cp-you {
        background: var(--accent-sage); color: #fff !important; font-size: 9.5px; font-weight: 800;
        padding: 1px 7px; border-radius: 20px; margin-left: 4px; letter-spacing: 0.4px;
    }
    .cp-text { font-size: 15.5px; line-height: 1.55; margin: 2px 0 8px 0; color: var(--text-dark); }
    .cp-stats { font-size: 12px; color: var(--text-muted) !important; margin-bottom: 4px; }
    .cp-composer {
        display: flex; align-items: center; gap: 10px; padding: 4px 2px 10px 2px;
        font-size: 13px; color: var(--text-muted) !important;
    }
    .cm-row { display: flex; gap: 9px; margin: 8px 0 2px 0; align-items: flex-start; }
    .cm-reply { margin-left: 38px; }
    .cm-avatar {
        width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-size: 16px; flex-shrink: 0;
    }
    .cm-bubble { background: var(--card-soft); border-radius: 4px 18px 18px 18px; padding: 7px 13px; max-width: 100%; }
    .cm-name { font-size: 12.5px; font-weight: 700; }
    .cm-text { font-size: 14px; line-height: 1.45; }
    .circle-online {
        display: inline-block; background: var(--accent-sage-light); border: 1px solid var(--border-soft);
        padding: 5px 13px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 10px;
    }

    /* ===================== SOFT, COMFORTING GAMES ===================== */
    .game-prompt {
        background: linear-gradient(135deg, var(--accent-sage-light) 0%, var(--card-soft) 100%);
        border: 1px solid var(--border-soft); border-radius: 22px; padding: 16px 14px;
        text-align: center; margin: 8px 0 12px 0; font-size: 15px; line-height: 2;
    }
    .game-chip {
        display: inline-block; background: var(--card-soft); border: 1px solid var(--border-soft);
        padding: 3px 11px; border-radius: 20px; font-size: 12px; font-weight: 700; margin: 0 6px 8px 0;
    }
    .letter-tile {
        display: inline-flex; align-items: center; justify-content: center; width: 38px; height: 44px; margin: 3px;
        background: var(--card-warm); border: 1px solid var(--border-soft); border-bottom: 3px solid var(--accent-sage);
        border-radius: 14px; font-size: 21px; font-weight: 800; color: var(--accent-sage) !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.05);
    }
    .num-bubble, .emoji-big {
        display: inline-flex; align-items: center; justify-content: center; margin: 4px;
        background: var(--card-warm); border: 1px solid var(--border-soft); border-radius: 50%;
        box-shadow: 0 3px 8px rgba(0,0,0,0.05);
    }
    .num-bubble { width: 50px; height: 50px; font-size: 19px; font-weight: 800; }
    .emoji-big { width: 58px; height: 58px; font-size: 30px; }
    .num-bubble.q, .emoji-big.q { background: var(--accent-sage-light); border: 2px dashed var(--accent-sage); color: var(--accent-sage) !important; font-weight: 800; }
    .flow-arrow { color: var(--accent-sage) !important; font-weight: 800; margin: 0 2px; }
    .word-chip {
        display: inline-block; padding: 4px 12px; margin: 3px; border-radius: 20px; font-size: 12.5px; font-weight: 700;
        background: var(--card-soft); border: 1px solid var(--border-soft); letter-spacing: 0.5px;
    }
    .word-chip.done { background: var(--accent-sage-light); border-color: var(--accent-sage); color: var(--accent-sage) !important; text-decoration: line-through; opacity: 0.85; }

    /* game cards & buttons (only inside the mini-game expanders) */
    div[data-testid="stExpander"] .stButton > button {
        min-height: 66px; font-size: 26px; border-radius: 22px !important;
        background: linear-gradient(160deg, var(--card-warm) 0%, var(--accent-sage-light) 100%) !important;
        border: 1px solid var(--border-soft) !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    div[data-testid="stExpander"] .stButton > button:hover { transform: translateY(-3px) scale(1.03); box-shadow: 0 8px 18px rgba(110,139,116,0.22); }
    div[data-testid="stExpander"] .stButton > button:disabled {
        background: linear-gradient(160deg, var(--accent-sage-light) 0%, var(--card-soft) 100%) !important;
        border-color: var(--accent-sage) !important; opacity: 0.9;
    }
    div[data-testid="stExpander"] button[kind="primary"],
    div[data-testid="stExpander"] button[data-testid="stBaseButton-primary"] {
        min-height: 44px; font-size: 15px; font-weight: 700; border-radius: 22px !important;
        background: var(--accent-sage) !important; border: none !important; color: #FFFFFF !important;
    }
    div[data-testid="stExpander"] button[kind="primary"] p,
    div[data-testid="stExpander"] button[data-testid="stBaseButton-primary"] p { color: #FFFFFF !important; font-size: 15px; }
    div[data-testid="stExpander"] div[role="radiogroup"] label p { font-size: 26px; }
    section[data-testid="stSidebar"] div[data-testid="stExpander"] .stButton > button {
        min-height: 36px; font-size: 13px; border-radius: 14px !important; box-shadow: none;
    }
    section[data-testid="stSidebar"] div[data-testid="stExpander"] .stButton > button:hover { transform: none; }
    /* keep game grids as grids on small screens */
    div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 0.5rem !important; }
    div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
    div[data-testid="stExpander"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { min-width: 0 !important; width: auto !important; flex: 1 1 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)



# ============================================================
# 6. BACKGROUND MUSIC (SELECTABLE TRACKS, LOOPING)
# ============================================================

MUSIC_WATCHER_HTML = """
<script>
(function() {
    var win = window.parent, doc = win.document;
    try {
        if (window.frameElement) {
            var holder = window.frameElement.closest('[data-testid="stElementContainer"]');
            if (holder) { holder.style.display = "none"; }
        }
    } catch (e) {}
    var code = "(" + function() {
        if (window.__mmMusic) { return; }
        window.__mmMusic = true;
        function hideBar(audio) {
            var box = audio.closest('[data-testid="stElementContainer"]') || audio.parentElement;
            if (box) { box.style.display = "none"; }
            document.querySelectorAll('.mm-music-label').forEach(function(label) {
                var lb = label.closest('[data-testid="stElementContainer"]') || label;
                lb.style.display = "none";
            });
        }
        window.setInterval(function() {
            var started = window.sessionStorage.getItem("mm_music_started") === "1";
            document.querySelectorAll('audio').forEach(function(audio) {
                if (!audio.dataset.mmBound) {
                    audio.dataset.mmBound = "1";
                    audio.loop = true;
                    audio.addEventListener("play", function() {
                        window.sessionStorage.setItem("mm_music_started", "1");
                        hideBar(audio);
                    });
                    if (started && audio.paused) { audio.play().catch(function() {}); }
                }
                if (started) { hideBar(audio); }
            });
        }, 400);
    }.toString() + ")();";
    var s = doc.createElement("script");
    s.text = code;
    doc.head.appendChild(s);
})();
</script>
"""

MUSIC_CONTROLS_HTML = """
<style>
  html, body { margin: 0; padding: 0; background: transparent; color: __FG__; color-scheme: __SCHEME__; }
  .mm-ctl { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; color: __FG__; }
  #pp { padding: 6px 14px; border-radius: 18px; border: 1px solid __ACCENT__; background: __BTN__; color: __FG__; cursor: pointer; font-size: 14px; }
  #pp:hover { background: __HOVER__; }
  #vol { accent-color: __ACCENT__; }
</style>
<div class="mm-ctl">
  <button id="pp">⏯ Play / Pause</button>
  <div style="margin-top:8px;">🔉 Volume <input id="vol" type="range" min="0" max="100" value="40" style="vertical-align:middle;width:140px;"></div>
</div>
<script>
(function() {
    var doc = window.parent.document;
    function audio() { return doc.querySelector('audio'); }
    document.getElementById("pp").onclick = function() {
        var a = audio(); if (!a) { return; }
        if (a.paused) { a.play().catch(function(){}); } else { a.pause(); }
    };
    document.getElementById("vol").oninput = function() {
        var a = audio(); if (a) { a.volume = this.value / 100; }
    };
    var a0 = audio(); if (a0) { document.getElementById("vol").value = Math.round(a0.volume * 100); }
})();
</script>
"""


def music_controls_html():
    dark = st.session_state.theme_mode == "dark"
    return (
        MUSIC_CONTROLS_HTML
        .replace("__FG__", "#ECEFED" if dark else "#2C3531")
        .replace("__SCHEME__", "dark" if dark else "light")
        .replace("__ACCENT__", "#8EAFA0" if dark else "#6E8B74")
        .replace("__BTN__", "#222C28" if dark else "#FFFFFF")
        .replace("__HOVER__", "#25332C" if dark else "#EBF1EC")
    )


def render_audio_controller():
    options = music_options()
    if not options:
        st.caption(f"🎵 No music found. Put an audio file here: {AUDIO_FILE}")
        return
    if st.session_state.music_choice not in options:
        st.session_state.music_choice = "🎧 Soothing (original)" if "🎧 Soothing (original)" in options else next(iter(options))

    chosen = options[st.session_state.music_choice]
    path = chosen["path"]
    if chosen["kind"] and not path.exists():
        with st.spinner("Preparing this calming sound (first time only)..."):
            try:
                generate_ambient_track(chosen["kind"], path)
            except Exception as err:
                st.caption(f"🎵 Could not prepare this sound: {err}")
                return
    try:
        audio_bytes = read_audio_bytes(str(path), path.stat().st_mtime)
    except Exception as err:
        st.caption(f"🎵 Could not read the music file ({err}). If it is in OneDrive, right-click it and choose 'Always keep on this device'.")
        return

    st.markdown('<div class="mm-music-label" style="font-size:12px; font-weight:700; margin-bottom:2px;">🎵 Calm background music (press play)</div>', unsafe_allow_html=True)
    try:
        st.audio(audio_bytes, format=chosen["mime"], loop=True, autoplay=True)
    except TypeError:
        st.audio(audio_bytes, format=chosen["mime"], loop=True)
    except Exception as err:
        st.caption(f"🎵 Music player could not load: {err}")

    # Hide the player bar once play is pressed (music keeps playing).
    components.html(MUSIC_WATCHER_HTML, height=0)

render_audio_controller()


# ============================================================
# 6b. INACTIVITY APP LOCK (15 MINUTES)
# ============================================================

IDLE_WATCHER_HTML = """
<script>
(function() {
    var win = window.parent, doc = win.document;
    try {
        if (window.frameElement) {
            var holder = window.frameElement.closest('[data-testid="stElementContainer"]');
            if (holder) { holder.style.display = "none"; }
        }
    } catch (e) {}
    var code = "(" + function() {
        window.__mmLastActive = Date.now();
        window.__mmIdleFired = false;
        window.__mmIdleLimit = __LIMIT_MS__;
        if (window.__mmIdleInstalled) { return; }
        window.__mmIdleInstalled = true;
        ["mousemove", "mousedown", "keydown", "touchstart", "scroll", "click"].forEach(function(ev) {
            document.addEventListener(ev, function() { window.__mmLastActive = Date.now(); }, {passive: true, capture: true});
        });
        window.setInterval(function() {
            if (window.__mmIdleFired) { return; }
            if (Date.now() - window.__mmLastActive >= window.__mmIdleLimit) {
                var btn = document.querySelector('.st-key-idle_lock_trigger button');
                if (btn) { window.__mmIdleFired = true; btn.click(); }
            }
        }, 5000);
    }.toString() + ")();";
    var s = doc.createElement("script");
    s.text = code;
    doc.head.appendChild(s);
})();
</script>
""".replace("__LIMIT_MS__", str(IDLE_LOCK_SECONDS * 1000))


def lock_app_now():
    st.session_state.app_locked = True


if st.session_state.user_registered:
    _now_ts = time.time()
    if st.session_state.last_activity is None:
        st.session_state.last_activity = _now_ts
    if not st.session_state.app_locked and _now_ts - st.session_state.last_activity > IDLE_LOCK_SECONDS:
        st.session_state.app_locked = True

    if st.session_state.app_locked:
        st.markdown(
            textwrap.dedent("""
            <div class="welcome-card">
                <div class="brand-small">MINDMATE IS LOCKED 🔒</div>
                <div class="welcome-title">Welcome back 🌿</div>
                <div class="welcome-subtitle">
                    For your privacy, MindMate locked itself after 15 minutes of inactivity.
                    Enter your first name to continue where you left off.
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )
        with st.form("unlock_form"):
            unlock_name = st.text_input("Your first name", placeholder="e.g. Alex")
            if st.form_submit_button("Unlock 🔓", use_container_width=True):
                expected = (st.session_state.student_name or "").strip().lower()
                if not expected or unlock_name.strip().lower() == expected:
                    st.session_state.app_locked = False
                    st.session_state.last_activity = time.time()
                    st.rerun()
                else:
                    st.error("That doesn't match. Please try again 🌿")
        st.stop()

    st.session_state.last_activity = _now_ts
    st.button("lock", key="idle_lock_trigger", on_click=lock_app_now)
    components.html(IDLE_WATCHER_HTML, height=0)


# ============================================================
# 7. CLICKABLE FLOATING MASCOT (STRICTLY HIDDEN ON LOGIN)
# ============================================================

if st.session_state.user_registered:
    if st.button("", key="floating_mascot_chat_trigger"):
        go_to("Chat")
        st.rerun()

    st.markdown(
        """
        <div class="mm-mascot-wrap">
            <div class="mm-mascot-stage">
                <svg class="mm-mascot-svg" viewBox="0 0 120 150" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <ellipse class="mm-shadow" cx="60" cy="144" rx="28" ry="5" fill="rgba(0,0,0,0.16)"/>
                    <g class="mm-legL">
                        <rect x="40" y="116" width="14" height="24" rx="7" fill="#5FBF86"/>
                        <ellipse cx="45" cy="140" rx="11" ry="5" fill="#46A471"/>
                    </g>
                    <g class="mm-legR">
                        <rect x="66" y="116" width="14" height="24" rx="7" fill="#5FBF86"/>
                        <ellipse cx="75" cy="140" rx="11" ry="5" fill="#46A471"/>
                    </g>
                    <g class="mm-armL">
                        <path d="M30 90 Q13 94 10 110" stroke="#5FBF86" stroke-width="10" stroke-linecap="round" fill="none"/>
                        <circle cx="10" cy="111" r="6.5" fill="#7ED6A0"/>
                    </g>
                    <g class="mm-armR">
                        <path d="M90 90 Q107 94 110 110" stroke="#5FBF86" stroke-width="10" stroke-linecap="round" fill="none"/>
                        <circle cx="110" cy="111" r="6.5" fill="#7ED6A0"/>
                    </g>
                    <ellipse cx="60" cy="86" rx="36" ry="40" fill="#7ED6A0" stroke="#4FB37A" stroke-width="2.5"/>
                    <ellipse cx="60" cy="102" rx="21" ry="19" fill="#C4EDD3"/>
                    <ellipse cx="60" cy="47" rx="14" ry="5" fill="#8B6B4A"/>
                    <path d="M60 46 L60 24" stroke="#3E9B5E" stroke-width="4" stroke-linecap="round"/>
                    <g class="mm-leaf">
                        <path d="M60 30 C 44 30, 35 20, 37 8 C 52 8, 60 17, 60 30 Z" fill="#4CC27B" stroke="#2F9A5C" stroke-width="1.5"/>
                        <path d="M60 25 C 76 25, 86 15, 84 3 C 69 3, 60 12, 60 25 Z" fill="#2FA862" stroke="#238A4D" stroke-width="1.5"/>
                    </g>
                    <g class="mm-eyes">
                        <circle cx="47" cy="80" r="5.5" fill="#1F4A37"/>
                        <circle cx="73" cy="80" r="5.5" fill="#1F4A37"/>
                        <circle cx="45" cy="78" r="1.8" fill="white"/>
                        <circle cx="71" cy="78" r="1.8" fill="white"/>
                    </g>
                    <ellipse cx="37" cy="93" rx="6" ry="4" fill="#F4B6B0" opacity="0.85"/>
                    <ellipse cx="83" cy="93" rx="6" ry="4" fill="#F4B6B0" opacity="0.85"/>
                    <path d="M51 94 Q60 104 69 94" stroke="#1F4A37" stroke-width="3" stroke-linecap="round" fill="none"/>
                </svg>
            </div>
            <div class="mm-cloud">Hi! Tap me to chat 🌿</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 8. HEADER & THEME TOGGLE (EXACTLY ONCE AT TOP LEVEL)
# ============================================================

header_c1, header_c2 = st.columns([7, 1])
with header_c1:
    with st.popover("🎵 Music"):
        _music_labels = list(music_options().keys())
        st.selectbox("Choose calming music", _music_labels, key="music_choice")
        components.html(music_controls_html(), height=90)
        st.caption("Add your own .mp3 files to the assets folder and they will appear here.")
with header_c2:
    theme_btn_label = "🌙 Dark" if st.session_state.theme_mode == "light" else "☀️ Light"
    if st.button(theme_btn_label, key="hdr_theme_toggle"):
        st.session_state.theme_mode = "dark" if st.session_state.theme_mode == "light" else "light"
        st.rerun()


# ============================================================
# 9. STUDENT ONBOARDING SYSTEM (LOGIN PAGE)
# ============================================================

if not st.session_state.user_registered:
    st.markdown(
        textwrap.dedent("""
        <div class="welcome-card">
            <div class="brand-small">WELCOME TO MINDMATE</div>
            <div class="welcome-title">Let's get started 🌿</div>
            <div class="welcome-subtitle">
                Enter your details to create your private space. Your name is used only during this session and is never stored in public records.
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown("### 🔑 Student Setup")
        student_name_input = st.text_input("First Name", placeholder="e.g. Alex")
        student_class_input = st.text_input("Grade / Class", placeholder="e.g. Class 10")
        generated_id = f"STU-{random.randint(10000, 99999)}"

        st.markdown("### 🤝 Trusted Adult Contact *(Optional)*")
        adult_name_in = st.text_input("Adult's Name", placeholder="e.g. Ms. Sarah")
        adult_relation_in = st.text_input("Relationship", placeholder="e.g. School Counsellor")
        adult_contact_in = st.text_input("Phone Number", placeholder="e.g. +1 555-0192")

        if st.button("Enter MindMate →", use_container_width=True):
            if student_name_input.strip() and student_class_input.strip():
                st.session_state.student_name = student_name_input.strip()
                st.session_state.student_id = generated_id
                st.session_state.student_class = student_class_input.strip()

                student_record = {
                    "Student_ID": generated_id,
                    "Name": "Anonymous",
                    "Class": student_class_input.strip(),
                }
                append_to_excel("01_Students", student_record)

                if adult_contact_in.strip():
                    adult_record = {
                        "Adult_ID": f"AD-{random.randint(1000, 9999)}",
                        "Student_ID": generated_id,
                        "Name": adult_name_in.strip() if adult_name_in.strip() else "Trusted Support",
                        "Relationship": adult_relation_in.strip() if adult_relation_in.strip() else "Support",
                        "Contact_Type": "Phone",
                        "Contact": adult_contact_in.strip(),
                    }
                    st.session_state.trusted_adult_info = adult_record
                    append_to_excel("09_Trusted_Adults", adult_record)

                st.session_state.user_registered = True
                st.rerun()
            else:
                st.error("Please enter your Name and Class to continue 🌿")
    st.stop()


# ============================================================
# 9b. HIDDEN LEFT SIDEBAR: SAVED BRAIN DUMP RECORDS
# ============================================================

with st.sidebar:
    st.markdown("### 📂 Records")
    st.caption("Every plan you complete in Brain Dump is saved here (like “Accounts exam”).")
    if not st.session_state.dump_records:
        st.info("No completed plans yet. Finish a plan of action and it will appear here 🌿")
    for rec in reversed(st.session_state.dump_records):
        with st.expander(f"✅ {rec['name']}"):
            st.caption(f"Completed: {rec['date']}")
            plan_info = rec.get("plan") or {}
            st.caption(f"{plan_info.get('difficulty', '')}  |  {plan_info.get('time', '')}")
            for heading, items in (rec.get("result") or {}).items():
                if items:
                    st.markdown(f"**{heading}**")
                    for item in items:
                        st.markdown(f"- {escape(item)}")
            if plan_info.get("steps"):
                st.markdown("**Plan of action**")
                for s_i, stp in enumerate(plan_info["steps"], 1):
                    st.markdown(f"{s_i}. ✅ {escape(stp)}")
            if st.button("🗑️ Delete record", key=f"del_{rec['id']}", use_container_width=True):
                st.session_state.dump_records = [r for r in st.session_state.dump_records if r["id"] != rec["id"]]
                st.rerun()


# ============================================================
# 10. CHAT MESSAGE QUEUE & PROCESSOR
# ============================================================

def queue_message(message):
    message = clean_value(message)
    if message:
        st.session_state.pending_message = message


def process_pending_message():
    message = clean_value(st.session_state.pending_message)
    if not message:
        return

    st.session_state.pending_message = None
    if chat_lock_status()[0]:
        return
    chat_track_activity()
    st.session_state.messages.append({"role": "user", "content": message})

    try:
        intent = predict_intent(message)
    except Exception:
        intent = "__fallback__"

    try:
        smart = build_smart_reply(message)
    except Exception:
        smart = {"text": generate_conversational_reply(message, st.session_state.messages),
                 "resources": [], "support": None, "severity": "none"}
    response = smart["text"]

    activity_id = None
    if not st.session_state.suppress_activities:
        if intent != "__fallback__":
            _, activity_id = get_response_for_intent(intent)
        if any(w in message.lower() for w in ["anxious", "panic", "breathe", "overwhelmed", "reset"]):
            activity_id = "ACT_01"

    if smart.get("severity") == "severe":
        activity_id = None

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "intent": intent,
        "activity_id": activity_id,
        "resources": smart.get("resources", []),
        "support": smart.get("support"),
    })
    chat_check_time_limits()


chat_is_locked, chat_lock_remaining, chat_lock_reason = False, 0, ""
if st.session_state.page == "Chat":
    if st.session_state.chat_prev_page != "Chat":
        chat_register_access()
    process_pending_message()
    chat_is_locked, chat_lock_remaining, chat_lock_reason = chat_lock_status()
st.session_state.chat_prev_page = st.session_state.page


# ============================================================
# 11. PAGE ROUTING ENGINE
# ============================================================

if st.session_state.page == "Home":
    student_disp_name = st.session_state.student_name if st.session_state.student_name else "there"
    st.markdown(
        textwrap.dedent(f"""
        <div class="welcome-card">
            <div class="brand-small">MINDMATE COMPANION</div>
            <div class="welcome-title">Hi {escape(student_disp_name)} 🌿</div>
            <div class="welcome-subtitle">
                Reset. Explore. Connect.<br>
                A warm space for everyday student feelings and small resets.
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )

    st.subheader("How are you feeling today?")

    mood_columns = st.columns(5)
    moods = [
        ("😊", "Good", 5),
        ("🙂", "Okay", 4),
        ("😐", "Meh", 3),
        ("😟", "Low", 2),
        ("😣", "Stressed", 1),
    ]

    for column, (emoji, mood, score) in zip(mood_columns, moods):
        with column:
            if st.button(f"{emoji}\n{mood}", key=f"mood_{mood}", use_container_width=True):
                today_date = datetime.now().strftime("%Y-%m-%d")
                st.session_state.mood = mood

                checkin_record = {
                    "Checkin_ID": f"MC-{int(time.time())}",
                    "Student_ID": st.session_state.student_id,
                    "Date": today_date,
                    "Mood": mood,
                    "Mood_Score": score,
                    "Optional_Note": "Home check-in",
                }

                st.session_state.mood_history.append({
                    "mood": mood,
                    "emoji": emoji,
                    "score": score,
                    "date": today_date,
                })

                append_to_excel("02_Mood_Checkins", checkin_record)
                st.rerun()

    if st.session_state.mood:
        st.markdown(
            textwrap.dedent(f"""
            <div class="mood-note">
                Thanks for checking in 🌿 You're feeling <strong>{escape(st.session_state.mood.lower())}</strong> today.
            </div>
            """),
            unsafe_allow_html=True,
        )

    with st.container():
        st.markdown("### 🧠 Brain Dump & Plan")
        st.write("De-clutter your mind and generate a step-by-step action plan.")
        if st.button("Start Brain Dump →", key="home_dump_btn", use_container_width=True):
            go_to("Brain Dump")
            st.rerun()

    with st.container():
        st.markdown("### 🌎 MindMate Circle")
        st.write("Share anonymous thoughts and see how other students are feeling.")
        if st.button("Visit Circle →", key="home_circle_btn", use_container_width=True):
            go_to("Circle")
            st.rerun()

    with st.container():
        st.markdown("### 🌿 Quick Reset")
        st.write("Try a short breathing or grounding activity when you need it.")
        if st.button("Explore activities →", key="home_act_btn", use_container_width=True):
            go_to("Activities")
            st.rerun()


elif st.session_state.page == "Chat" and not chat_is_locked:
    st.markdown('<div class="brand-small">MINDMATE CHAT</div>', unsafe_allow_html=True)
    st.title("💬 Talk to MindMate")

    if not st.session_state.messages:
        with st.container():
            st.markdown("### Hi, I'm listening 🌿")
            st.write("Tap a starter prompt or type your own:")
            example_messages = [
                "I'm feeling stressed about exams",
                "I can't study properly and feel overwhelmed",
                "I feel really tired and burned out",
                "Just talk to me, don't suggest any activity",
            ]
            for idx, ex in enumerate(example_messages):
                if st.button(ex, key=f"ex_{idx}", use_container_width=True):
                    queue_message(ex)
                    st.rerun()

    for index, message in enumerate(st.session_state.messages):
        role = message.get("role")
        content = safe_text(message.get("content"), "")

        if role == "user":
            st.markdown(
                textwrap.dedent(f"""
                <div class="chat-user">
                    <div class="chat-user-bubble">{escape(content).replace(chr(10), "<br>")}</div>
                </div>
                """),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                textwrap.dedent(f"""
                <div class="chat-ai">
                    <div>
                        <div class="chat-label">MINO 🌿</div>
                        <div class="chat-ai-bubble">{escape(content).replace(chr(10), "<br>")}</div>
                    </div>
                </div>
                """),
                unsafe_allow_html=True,
            )

            render_message_extras(message, index)

            activity_id = message.get("activity_id")
            if activity_id and not st.session_state.suppress_activities:
                act = get_activity(activity_id)
                act_title = activity_name(act) if act is not None else "1-Minute Breathing Reset"
                act_desc = activity_description(act) if act is not None else "Inhale gently for 4s, hold 2s, exhale 6s."
                act_dur = activity_duration(act) if act is not None else 1
                guidance_steps = get_activity_guidance(act_title, act_desc)

                with st.container():
                    st.markdown(f"### 🌿 Guided Reset: {act_title}")
                    st.write(act_desc)

                    with st.expander("📋 Click to view step-by-step instructions"):
                        for s_idx, step in enumerate(guidance_steps, 1):
                            st.markdown(
                                f'<div class="step-item-card"><b>Step {s_idx}:</b> {escape(step)}</div>',
                                unsafe_allow_html=True,
                            )

                    timer_key = f"timer_{index}_{activity_id}"
                    col_t1, col_t2 = st.columns([1, 1])

                    with col_t1:
                        if st.button(f"⏱️ Start ({act_dur}m)", key=f"start_{timer_key}", use_container_width=True):
                            st.session_state.active_timer_id = timer_key
                            st.session_state.timer_seconds_left = act_dur * 60
                            st.session_state.timer_running = True
                            st.rerun()

                    with col_t2:
                        if st.button("🔄 Reset Timer", key=f"reset_{timer_key}", use_container_width=True):
                            if st.session_state.active_timer_id == timer_key:
                                st.session_state.timer_running = False
                                st.session_state.active_timer_id = None
                            st.rerun()

                    if st.session_state.active_timer_id == timer_key and st.session_state.timer_running:
                        t_placeholder = st.empty()
                        while st.session_state.timer_seconds_left > 0 and st.session_state.timer_running:
                            m_rem, s_rem = divmod(st.session_state.timer_seconds_left, 60)
                            t_placeholder.info(f"⏳ Time Remaining: **{m_rem:02d}:{s_rem:02d}**")
                            time.sleep(1)
                            st.session_state.timer_seconds_left -= 1
                        if st.session_state.timer_seconds_left == 0:
                            t_placeholder.success("✨ Great job completing this reset!")
                            st.session_state.timer_running = False

    def send_message_callback():
        user_text = st.session_state.temp_message_input.strip()
        if user_text:
            queue_message(user_text)
            st.session_state.temp_message_input = ""

    st.markdown("<br>", unsafe_allow_html=True)
    input_col, send_col = st.columns([5, 1], vertical_alignment="bottom")
    with input_col:
        st.text_input(
            "Message MindMate",
            placeholder="Type what's on your mind...",
            key="temp_message_input",
            label_visibility="collapsed",
            on_change=send_message_callback,
        )
    with send_col:
        st.button("➤", key="send_chat_message", use_container_width=True, on_click=send_message_callback)


elif st.session_state.page == "Chat" and chat_is_locked:
    st.markdown('<div class="brand-small">MINDMATE CHAT</div>', unsafe_allow_html=True)
    st.title("💬 Talk to MindMate")
    render_chat_lock_screen(chat_lock_remaining, chat_lock_reason)


elif st.session_state.page == "Activities":
    st.markdown('<div class="brand-small">RESET</div>', unsafe_allow_html=True)
    st.title("🌿 Guided Reset Activities")

    activities_list = [
        {"name": "1-minute breathing reset", "dur": 1, "desc": "Inhale quietly for 4s, hold for 2s, exhale for 6s."},
        {"name": "5-minute brain dump", "dur": 5, "desc": "Write down everything on your mind without filtering."},
        {"name": "grounding check-in", "dur": 3, "desc": "Identify 5 things you see, 4 touch, 3 hear, 2 smell, 1 breath."},
        {"name": "box breathing", "dur": 2, "desc": "Breathe in a calm square: 4 seconds in, hold, out, hold."},
        {"name": "neck & shoulder release", "dur": 2, "desc": "Loosen the tension that builds up while studying."},
        {"name": "three good things", "dur": 2, "desc": "Notice three small things that went okay today."},
        {"name": "body scan relaxation", "dur": 4, "desc": "Slowly relax your body from head to toe."},
        {"name": "mindful water break", "dur": 1, "desc": "Hydrate slowly and give your mind a tiny pause."},
    ]

    for idx, act in enumerate(activities_list):
        name = act["name"]
        desc = act["desc"]
        dur = act["dur"]
        steps = get_activity_guidance(name, desc)

        with st.container():
            st.markdown(f"### 🌿 {name.title()} ({dur} min)")
            st.write(desc)

            with st.expander("📋 Click to view step-by-step instructions"):
                for s_i, stp in enumerate(steps, 1):
                    st.markdown(
                        f'<div class="step-item-card"><b>Step {s_i}:</b> {escape(stp)}</div>',
                        unsafe_allow_html=True,
                    )

            act_timer_key = f"act_page_timer_{idx}"
            c_a1, c_a2 = st.columns([1, 1])

            with c_a1:
                if st.button(f"⏱️ Start {dur}-Min Timer", key=f"start_{act_timer_key}", use_container_width=True):
                    st.session_state.active_timer_id = act_timer_key
                    st.session_state.timer_seconds_left = dur * 60
                    st.session_state.timer_running = True
                    st.rerun()

            with c_a2:
                if st.button("🔄 Reset Timer", key=f"reset_{act_timer_key}", use_container_width=True):
                    if st.session_state.active_timer_id == act_timer_key:
                        st.session_state.timer_running = False
                        st.session_state.active_timer_id = None
                    st.rerun()

            if st.session_state.active_timer_id == act_timer_key and st.session_state.timer_running:
                t_place = st.empty()
                while st.session_state.timer_seconds_left > 0 and st.session_state.timer_running:
                    m_rem, s_rem = divmod(st.session_state.timer_seconds_left, 60)
                    t_place.info(f"⏳ Time Remaining: **{m_rem:02d}:{s_rem:02d}**")
                    time.sleep(1)
                    st.session_state.timer_seconds_left -= 1
                if st.session_state.timer_seconds_left == 0:
                    t_place.success("✨ Activity Timer Complete!")
                    st.session_state.timer_running = False


elif st.session_state.page == "Brain Dump":
    st.markdown('<div class="brand-small">CLEAR YOUR HEAD</div>', unsafe_allow_html=True)
    st.title("🧠 Brain Dump")

    # Fresh start after a completed plan (clears old input, plan and ticks)
    if st.session_state.dump_reset_pending:
        st.session_state["dump_text_type"] = ""
        st.session_state["dump_text_pen"] = ""
        for _k in [k for k in list(st.session_state.keys()) if str(k).startswith("step_chk_")]:
            del st.session_state[_k]
        st.session_state.plan_checkins = {}
        st.session_state.brain_dump_result = None
        st.session_state.brain_dump_plan = None
        st.session_state.brain_dump_raw = ""
        st.session_state.dump_reset_pending = False

    if st.session_state.dump_just_completed:
        saved_name = st.session_state.dump_just_completed
        st.session_state.dump_just_completed = None
        st.balloons()
        st.markdown(
            """
            <div class="completion-banner">
                WAY TO GO!! YOU COMPLETED YOUR PLAN OF ACTION AND ARE READYY 🎉
            </div>
            """,
            unsafe_allow_html=True
        )
        st.success(f"📂 Saved to your Records (left sidebar) as “{saved_name}”. Your Brain Dump is fresh and ready for a new one 🌿")

    st.write("Dump everything in your head. Don't organize it.")

    dm_col1, dm_col2 = st.columns(2)
    with dm_col1:
        if st.button("⌨️ Type Notes", key="mode_type_pill", use_container_width=True):
            st.session_state.dump_mode = "type"
            st.rerun()
    with dm_col2:
        if st.button("✍️ Pen / Stylus Canvas", key="mode_pen_pill", use_container_width=True):
            st.session_state.dump_mode = "pen"
            st.rerun()

    st.markdown("---")
    brain_dump_text = ""

    if st.session_state.dump_mode == "pen":
        st.caption("Use your stylus or finger to write notes:")
        if CANVAS_AVAILABLE:
            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0)",
                stroke_width=3,
                stroke_color="#ECEFED" if st.session_state.theme_mode == "dark" else "#121816",
                background_color="#1A2320" if st.session_state.theme_mode == "dark" else "#FFFFFF",
                height=200,
                drawing_mode="freedraw",
                key="brain_dump_canvas_main",
            )
        brain_dump_text = st.text_area(
            "Transcribe key notes from your handwriting above:",
            placeholder="Accounts exam in 2 hours have 4 chaps in it, need to talk to counsellor...",
            height=100,
            key="dump_text_pen",
        )
    else:
        brain_dump_text = st.text_area(
            "Dump your thoughts here:",
            placeholder="Accounts exam in 2 hours have 4 chaps in it, need to talk to counsellor...",
            height=160,
            key="dump_text_type",
        )

    if st.button("Organize my thoughts ✨", use_container_width=True):
        if brain_dump_text.strip():
            st.session_state.brain_dump_result = organize_brain_dump(brain_dump_text)
            st.session_state.brain_dump_raw = brain_dump_text
            st.session_state.brain_dump_plan = None
            st.rerun()

    if st.session_state.brain_dump_result:
        result = st.session_state.brain_dump_result
        total_items = sum(len(items) for items in result.values())
        urgent_count = len(result.get("URGENT", []))
        today_count = min(urgent_count, 2) if urgent_count else min(total_items, 1)

        st.markdown("---")
        st.markdown("### Your brain → Organized")

        for heading, items in result.items():
            with st.container():
                st.markdown(f"**{heading}**")
                if items:
                    for item in items:
                        st.markdown(f"- {escape(item)}")
                else:
                    st.caption("Nothing here right now.")

        st.markdown(f"**“You had {total_items} things competing for your attention. Focus on {today_count} priority items first.”**")

        st.markdown("---")
        st.markdown("### 📋 Custom Plan of Action")

        if not st.session_state.brain_dump_plan:
            with st.form("plan_generator_form"):
                subject_diff = st.selectbox("Academic Difficulty:", ["🌶️ High Difficulty", "⚡ Moderate Focus", "🟢 Quick Review"])
                time_est = st.selectbox("Time Available Today:", ["⏱️ Under 30 mins", "⏱️ 30-60 mins", "⏱️ 1-2 hours", "⏱️ 2+ hours"])
                if st.form_submit_button("Generate Step-by-Step Action Plan 🚀", use_container_width=True):
                    urgent_items = result.get("URGENT", [])
                    primary_task = urgent_items[0] if urgent_items else "Top Task"
                    st.session_state.brain_dump_plan = {
                        "difficulty": subject_diff,
                        "time": time_est,
                        "steps": [
                            f"Priority Focus: {primary_task}",
                            "Take a 5-minute Mindfulness Reset",
                            "Work through secondary items",
                            "Review progress & wrap up"
                        ]
                    }
                    st.rerun()
        else:
            plan = st.session_state.brain_dump_plan
            st.info(f"**Difficulty:** {plan['difficulty']} | **Time Available:** {plan['time']}")
            completed_steps = 0
            for idx, step in enumerate(plan["steps"]):
                chk_key = f"step_chk_{idx}"
                
                if "Mindfulness Reset" in step or "breathing" in step.lower():
                    c_step1, c_step2 = st.columns([3, 1])
                    with c_step1:
                        is_checked = st.checkbox(f"**Step {idx+1}:** {step}", key=chk_key, value=st.session_state.plan_checkins.get(chk_key, False))
                    with c_step2:
                        if st.button("🌿 Do Reset Now", key=f"poa_reset_btn_{idx}"):
                            go_to("Activities")
                            st.rerun()
                else:
                    is_checked = st.checkbox(f"**Step {idx+1}:** {step}", key=chk_key, value=st.session_state.plan_checkins.get(chk_key, False))

                st.session_state.plan_checkins[chk_key] = is_checked
                if is_checked:
                    completed_steps += 1

            progress = completed_steps / len(plan["steps"])
            st.progress(progress)

            if completed_steps == len(plan["steps"]):
                # Save the finished plan to the Records sidebar, then restore a fresh Brain Dump
                saved_record = save_dump_record(result, plan)
                st.session_state.dump_just_completed = saved_record["name"]
                st.session_state.dump_reset_pending = True
                st.rerun()


elif st.session_state.page == "Explore":
    st.markdown('<div class="brand-small">DISCOVER</div>', unsafe_allow_html=True)

    if st.session_state.selected_resource_id:
        res_info = get_resource_details(st.session_state.selected_resource_id)

        if st.button("← Back to All Resources", use_container_width=True):
            st.session_state.selected_resource_id = None
            st.rerun()

        st.title(f"📖 {res_info['title']}")
        st.write(res_info["description"])

        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            if st.button("📰 Articles", key="res_pill_art", use_container_width=True):
                st.session_state.res_content_type = "articles"
                st.rerun()
        with rc2:
            if st.button("📚 Books", key="res_pill_bk", use_container_width=True):
                st.session_state.res_content_type = "books"
                st.rerun()
        with rc3:
            if st.button("📺 Videos", key="res_pill_vid", use_container_width=True):
                st.session_state.res_content_type = "videos"
                st.rerun()

        st.markdown("---")

        if st.session_state.res_content_type == "articles":
            st.markdown("### 📰 Curated Articles & Guides")
            for art in res_info["articles"]:
                with st.container():
                    st.markdown(f"#### 📄 {art['title']}")
                    st.write(art["desc"])
                    st.markdown(f"[Read Full Article 🔗]({art['url']})")

        elif st.session_state.res_content_type == "videos":
            st.markdown("### 📺 Video Guides")
            for vid in res_info["videos"]:
                with st.container():
                    st.image(vid["thumb"], use_container_width=True)
                    st.markdown(f"#### 🎬 [{vid['title']}]({vid['url']})")

        elif st.session_state.res_content_type == "books":
            st.markdown("### 📚 Recommended Books")
            for bk in res_info["books"]:
                with st.container():
                    c_img, c_txt = st.columns([1, 2])
                    with c_img:
                        st.image(bk["image"], use_container_width=True)
                    with c_txt:
                        st.markdown(f"#### {bk['title']}")
                        st.caption(f"Author: {bk['author']}")
                        st.markdown(f"[View on Amazon 🛒]({bk['amazon']})")

    else:
        st.title("✨ Resources & Explore")

        exp_pill_1, exp_pill_2 = st.columns(2)
        with exp_pill_1:
            if st.button("📚 Resources", key="exp_tab_res", use_container_width=True):
                st.session_state.explore_tab = "resources"
                st.rerun()
        with exp_pill_2:
            if st.button("🎮 Mini-Games", key="exp_tab_gms", use_container_width=True):
                st.session_state.explore_tab = "games"
                st.rerun()

        st.markdown("---")

        if st.session_state.explore_tab == "resources":
            res_list = [
                {"Title": "Understanding Everyday Stress", "Category": "Mental Health", "Type": "Guide", "Description": "How stress affects your body and mind."},
                {"Title": "Overcoming Exam Anxiety", "Category": "Academics", "Type": "Article", "Description": "Practical strategies to stay calm before tests."},
                {"Title": "Improving Sleep Quality", "Category": "Wellness", "Type": "Tips", "Description": "Build a night routine for restful sleep."},
                {"Title": "Coping with Sadness & Loneliness", "Category": "Emotions", "Type": "Guide", "Description": "Gentle support for low days and lonely moments."},
                {"Title": "Friendships, Bullying & Peer Pressure", "Category": "Relationships", "Type": "Guide", "Description": "Handle bullying, cliques and friendship troubles."},
                {"Title": "Focus, Motivation & Screen Time", "Category": "Habits", "Type": "Tips", "Description": "Beat procrastination and take back your attention."}
            ]
            for res in res_list:
                with st.container():
                    st.markdown(f"### 📖 {res['Title']}")
                    st.caption(f"Category: **{res['Category']}** • Type: **{res['Type']}**")
                    st.write(res["Description"])
                    if st.button("View Resource Details →", key=f"res_{res['Title']}", use_container_width=True):
                        st.session_state.selected_resource_id = res['Title']
                        st.rerun()

        else:
            st.markdown("### 🎮 Relaxation Mini-Games")
            st.caption("No timers, no pressure. Every round gives you a fresh puzzle 🌿")

            # ---------------- GAME 1: MEMORY MATCH ----------------
            with st.expander("🧩 GAME 1: Memory Match"):
                st.markdown('<div class="game-badge">MEMORY LEVEL</div>', unsafe_allow_html=True)
                if not st.session_state.memory_cards:
                    new_memory_game()

                total_cards = len(st.session_state.memory_cards)
                st.markdown(
                    f'<span class="game-chip">🌱 Level {st.session_state.memory_level}</span>'
                    f'<span class="game-chip">👣 Moves {st.session_state.memory_moves}</span>'
                    f'<span class="game-chip">💚 Pairs {len(st.session_state.memory_matched) // 2}/{total_cards // 2}</span>',
                    unsafe_allow_html=True,
                )
                game_feedback_show("memory")

                cols = st.columns(4)
                for idx_c, card_emoji in enumerate(st.session_state.memory_cards):
                    with cols[idx_c % 4]:
                        if idx_c in st.session_state.memory_matched:
                            st.button(f"{card_emoji}", key=f"mem_done_{idx_c}", disabled=True, use_container_width=True)
                        elif idx_c in st.session_state.memory_flipped:
                            st.button(f"{card_emoji}", key=f"mem_flip_{idx_c}", use_container_width=True)
                        else:
                            if st.button("🌿", key=f"mem_btn_{idx_c}", use_container_width=True):
                                if len(st.session_state.memory_flipped) >= 2:
                                    st.session_state.memory_flipped = []
                                st.session_state.memory_flipped.append(idx_c)
                                if len(st.session_state.memory_flipped) == 2:
                                    st.session_state.memory_moves += 1
                                    i1, i2 = st.session_state.memory_flipped
                                    if st.session_state.memory_cards[i1] == st.session_state.memory_cards[i2]:
                                        st.session_state.memory_matched.extend([i1, i2])
                                        st.session_state.memory_flipped = []
                                st.rerun()

                if len(st.session_state.memory_matched) == total_cards and total_cards > 0:
                    st.success(f"🎉 Lovely! You matched every pair in {st.session_state.memory_moves} moves.")
                    if st.button("Next level →", key="mem_next", type="primary", use_container_width=True):
                        st.session_state.memory_level += 1
                        new_memory_game()
                        game_say("memory", "ok", f"🌱 Level {st.session_state.memory_level}: new cards, freshly shuffled!")
                        st.rerun()
                else:
                    if len(st.session_state.memory_flipped) == 2:
                        st.caption("Not a match this time. Tap any card to try again 🌿")
                    if st.button("🔀 Shuffle new cards", key="mem_shuffle", type="primary", use_container_width=True):
                        new_memory_game()
                        st.rerun()

            # ---------------- GAME 2: WORD SCRAMBLE ----------------
            with st.expander("🔤 GAME 2: Word Scramble"):
                st.markdown('<div class="game-badge">WORD FOCUS</div>', unsafe_allow_html=True)
                if not st.session_state.scramble_word:
                    new_scramble()

                st.markdown(f'<span class="game-chip">🌟 Words solved: {st.session_state.scramble_score}</span>', unsafe_allow_html=True)
                game_feedback_show("scramble")
                tiles = "".join(f'<span class="letter-tile">{escape(ch)}</span>' for ch in st.session_state.scramble_jumbled)
                st.markdown(f'<div class="game-prompt">Unscramble these letters<br>{tiles}</div>', unsafe_allow_html=True)

                round_id = st.session_state.scramble_round
                guess_in = st.text_input("Your Answer:", key=f"scramble_guess_{round_id}", placeholder="Type the word here...")
                if st.checkbox("💡 Show me the first letter", key=f"scramble_hint_{round_id}"):
                    st.caption(f"It starts with **{st.session_state.scramble_word[0]}** and has {len(st.session_state.scramble_word)} letters.")

                sc1, sc2 = st.columns(2)
                with sc1:
                    if st.button("Submit Word", key="scramble_sub", type="primary", use_container_width=True):
                        if guess_in.strip().upper() == st.session_state.scramble_word:
                            st.session_state.scramble_score += 1
                            solved = st.session_state.scramble_word
                            new_scramble()
                            game_say("scramble", "ok", f"✨ Correct, it was {solved}! Here's a brand new word.")
                            st.rerun()
                        else:
                            st.info("Close! Take a breath and try again 🌿")
                with sc2:
                    if st.button("↻ Skip to new word", key="scramble_skip", type="primary", use_container_width=True):
                        new_scramble()
                        st.rerun()

            # ---------------- GAME 3: QUICK PATTERN ----------------
            with st.expander("🔢 GAME 3: Quick Pattern"):
                st.markdown('<div class="game-badge">LOGIC PATTERN</div>', unsafe_allow_html=True)
                if not st.session_state.pattern_seq:
                    new_pattern()

                st.markdown(f'<span class="game-chip">🌟 Patterns solved: {st.session_state.pattern_score}</span>', unsafe_allow_html=True)
                game_feedback_show("pattern")
                bubbles = "".join(f'<span class="num-bubble">{n}</span>' for n in st.session_state.pattern_seq)
                st.markdown(
                    f'<div class="game-prompt">What number comes next?<br>{bubbles}<span class="num-bubble q">?</span></div>',
                    unsafe_allow_html=True,
                )
                p_round = st.session_state.pattern_round
                p_guess = st.number_input("Your Answer:", step=1, key=f"pat_guess_{p_round}")
                if st.checkbox("💡 Need a hint?", key=f"pat_hint_{p_round}"):
                    st.caption(st.session_state.pattern_hint)

                pc1, pc2 = st.columns(2)
                with pc1:
                    if st.button("Submit Pattern", key="pat_sub", type="primary", use_container_width=True):
                        if p_guess == st.session_state.pattern_answer:
                            st.session_state.pattern_score += 1
                            new_pattern()
                            game_say("pattern", "ok", "🎉 Correct pattern! Here's a new one.")
                            st.rerun()
                        else:
                            st.info("Almost! Look at how the numbers change from one to the next 🌿")
                with pc2:
                    if st.button("↻ New pattern", key="pat_new", type="primary", use_container_width=True):
                        new_pattern()
                        st.rerun()

            # ---------------- GAME 4: EMOJI SEQUENCE ----------------
            with st.expander("😃 GAME 4: Emoji Sequence"):
                st.markdown('<div class="game-badge">VISUAL SEQUENCE</div>', unsafe_allow_html=True)
                if not st.session_state.emoji_seq:
                    new_emoji()

                st.markdown(f'<span class="game-chip">🌟 Flows completed: {st.session_state.emoji_score}</span>', unsafe_allow_html=True)
                game_feedback_show("emoji")
                flow = '<span class="flow-arrow">➔</span>'.join(f'<span class="emoji-big">{e}</span>' for e in st.session_state.emoji_seq)
                st.markdown(
                    f'<div class="game-prompt">Complete the flow<br>{flow}<span class="flow-arrow">➔</span><span class="emoji-big q">?</span></div>',
                    unsafe_allow_html=True,
                )
                e_round = st.session_state.emoji_round
                e_choice = st.radio("Next Emoji:", st.session_state.emoji_options, horizontal=True, key=f"e_rad_{e_round}", index=None)

                ec1, ec2 = st.columns(2)
                with ec1:
                    if st.button("Check Emoji", key="e_sub", type="primary", use_container_width=True):
                        if e_choice is None:
                            st.info("Pick an emoji first 🌿")
                        elif e_choice == st.session_state.emoji_answer:
                            st.session_state.emoji_score += 1
                            new_emoji()
                            game_say("emoji", "ok", "✨ Beautiful flow! Here's a new sequence.")
                            st.rerun()
                        else:
                            st.info("Not quite. Think about what naturally comes next 🌿")
                with ec2:
                    if st.button("↻ New sequence", key="e_new", type="primary", use_container_width=True):
                        new_emoji()
                        st.rerun()

            # ---------------- GAME 5: ODD ONE OUT ----------------
            with st.expander("🔍 GAME 5: Odd One Out"):
                st.markdown('<div class="game-badge">OBSERVATION</div>', unsafe_allow_html=True)
                if not st.session_state.odd_items:
                    new_odd()

                st.markdown(f'<span class="game-chip">🌟 Spotted: {st.session_state.odd_score}</span>', unsafe_allow_html=True)
                game_feedback_show("odd")
                st.markdown('<div class="game-prompt">Which one doesn\'t belong with the others?</div>', unsafe_allow_html=True)
                o_round = st.session_state.odd_round
                o_choice = st.radio("Odd Item:", st.session_state.odd_items, horizontal=True, key=f"odd_rad_{o_round}", index=None)

                oc1, oc2 = st.columns(2)
                with oc1:
                    if st.button("Confirm Choice", key="odd_sub", type="primary", use_container_width=True):
                        if o_choice is None:
                            st.info("Pick one first 🌿")
                        elif o_choice == st.session_state.odd_answer:
                            st.session_state.odd_score += 1
                            new_odd()
                            game_say("odd", "ok", "🎉 Sharp observation! Here's a new set.")
                            st.rerun()
                        else:
                            st.info("Hmm, look again. Which one is from a different group? 🌿")
                with oc2:
                    if st.button("↻ New set", key="odd_new", type="primary", use_container_width=True):
                        new_odd()
                        st.rerun()

            # ---------------- GAME 6: MINI WORD CROSSWORD (DRAG TO SELECT) ----------------
            with st.expander("🧩 GAME 6: Mini Word Crossword"):
                st.markdown('<div class="game-badge">WORD CROSSWORD</div>', unsafe_allow_html=True)
                if not st.session_state.crossword_grid:
                    new_wordsearch()

                cw_words = st.session_state.crossword_words
                cw_found = st.session_state.crossword_found_words
                st.markdown(
                    f'<span class="game-chip">🌱 Level {st.session_state.crossword_level}</span>'
                    f'<span class="game-chip">🔎 Found {len(cw_found)}/{len(cw_words)}</span>',
                    unsafe_allow_html=True,
                )
                game_feedback_show("crossword")
                chips = "".join(
                    f'<span class="word-chip{" done" if w in cw_found else ""}">{escape(w)}</span>' for w in cw_words
                )
                st.markdown(f'<div style="margin-bottom:6px;">{chips}</div>', unsafe_allow_html=True)
                st.caption("✏️ Press and drag across the letters to draw a line over a hidden word (works with mouse or finger).")

                if mm_wordsearch is None:
                    st.warning("The drag-to-select board could not load on this device.")
                else:
                    ws_val = mm_wordsearch(
                        grid=st.session_state.crossword_grid,
                        words=cw_words,
                        found=cw_found,
                        segments=st.session_state.crossword_segments,
                        dark=(st.session_state.theme_mode == "dark"),
                        key=f"mm_ws_{st.session_state.crossword_round}",
                        default=None,
                    )
                    if (
                        isinstance(ws_val, dict)
                        and ws_val.get("nonce")
                        and ws_val.get("nonce") != st.session_state.crossword_last_nonce
                    ):
                        st.session_state.crossword_last_nonce = ws_val["nonce"]
                        picked = str(ws_val.get("word", "")).upper()
                        if picked in cw_words and picked not in cw_found:
                            cw_found.append(picked)
                            st.session_state.crossword_segments.append({
                                "word": picked,
                                "r1": ws_val.get("r1"), "c1": ws_val.get("c1"),
                                "r2": ws_val.get("r2"), "c2": ws_val.get("c2"),
                            })
                            st.rerun()

                if cw_words and len(cw_found) == len(cw_words):
                    st.success("🎉 You found every word! Take a calm breath, you did great.")
                    if st.button("Next puzzle →", key="cw_next", type="primary", use_container_width=True):
                        st.session_state.crossword_level += 1
                        new_wordsearch()
                        game_say("crossword", "ok", f"🌱 Level {st.session_state.crossword_level}: a brand new set of words!")
                        st.rerun()
                else:
                    if st.button("🔀 New puzzle (new words)", key="cw_shuffle", type="primary", use_container_width=True):
                        new_wordsearch()
                        st.rerun()


elif st.session_state.page == "Circle":
    st.markdown('<div class="brand-small">YOU ARE NOT ALONE</div>', unsafe_allow_html=True)
    st.title("🌎 MindMate Circle")
    st.write("A shared space for student feelings. Post, support and cheer each other on, all anonymously.")

    circle_data = load_circle_data()
    online_peers = random.randint(18, 42)
    st.markdown(f'<span class="circle-online">🟢 {online_peers} anonymous students online</span>', unsafe_allow_html=True)

    my_emoji, my_alias, my_color = circle_identity(st.session_state.student_id or "me")

    with st.container():
        st.markdown(
            f'<div class="cp-head"><div class="cp-avatar" style="background:{my_color}">{my_emoji}</div>'
            f'<div><div class="cp-name">What\'s on your mind?</div>'
            f'<div class="cp-time">Posting anonymously as {escape(my_alias)}</div></div></div>',
            unsafe_allow_html=True,
        )
        with st.form("circle_post_form", clear_on_submit=True):
            post_text = st.text_area("Your anonymous thought", placeholder="Studied for hours and still feeling nervous...", max_chars=280, label_visibility="collapsed")
            if st.form_submit_button("Post anonymously", use_container_width=True):
                cleaned_post = post_text.strip()
                if cleaned_post and circle_post_is_appropriate(cleaned_post):
                    circle_data["posts"].append({
                        "id": f"P-{int(time.time() * 1000)}",
                        "text": cleaned_post,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "ts": time.time(),
                        "sid": st.session_state.student_id,
                        "reactions": {"❤️ Same here": 1, "🫂 You're not alone": 1},
                        "comments": [],
                    })
                    save_circle_data(circle_data)
                    st.success("Your thought is now in the Circle.")
                    st.rerun()
                elif cleaned_post:
                    st.warning("Please keep personal details private so everyone stays safe 🌿")

    feed_sort = st.radio("Sort feed", ["🕒 Latest", "💚 Most supported"], horizontal=True, label_visibility="collapsed", key="circle_sort")
    st.markdown("### 🫂 Notes from other students")

    if feed_sort.startswith("🕒"):
        posts = sorted(circle_data["posts"], key=lambda p: (p.get("date", ""), p.get("ts", 0), p.get("id", "")), reverse=True)
    else:
        posts = sorted(
            circle_data["posts"],
            key=lambda p: sum(p.get("reactions", {}).values()) + 2 * len(p.get("comments", [])),
            reverse=True,
        )

    R1, R2, R3 = "❤️ Same here", "🫂 You're not alone", "🔥 We got this"

    for post in posts[:20]:
        pid = post["id"]
        p_emoji, p_alias, p_color = circle_identity(post.get("sid") or pid)
        you_badge = ' <span class="cp-you">You</span>' if post.get("sid") and post.get("sid") == st.session_state.student_id else ""
        reactions = post.get("reactions", {})
        comments = post.get("comments", [])
        total_comments = sum(1 + len(c.get("replies", [])) for c in comments)
        total_reactions = sum(reactions.values())
        post_body = escape(post.get("text", "")).replace("\n", "<br>")

        with st.container(border=True):
            st.markdown(
                f'<div class="cp-head"><div class="cp-avatar" style="background:{p_color}">{p_emoji}</div>'
                f'<div><div class="cp-name">{escape(p_alias)}{you_badge}</div>'
                f'<div class="cp-time">{escape(circle_time_label(post))}</div></div></div>'
                f'<div class="cp-text">{post_body}</div>'
                f'<div class="cp-stats">💚 {total_reactions} support • 💬 {total_comments} comments</div>',
                unsafe_allow_html=True,
            )

            col_r1, col_r2, col_r3, col_cm, col_dm = st.columns([1, 1, 1, 1, 1.3])
            with col_r1:
                liked = f"{pid}|None|None|{R1}" in st.session_state.circle_liked
                st.button(f"{'💖' if liked else '❤️'} {reactions.get(R1, 0)}", key=f"r1_{pid}", help="Same here",
                          on_click=circle_toggle_like, args=(pid, None, None, R1), use_container_width=True)
            with col_r2:
                liked = f"{pid}|None|None|{R2}" in st.session_state.circle_liked
                st.button(f"{'🤗' if liked else '🫂'} {reactions.get(R2, 0)}", key=f"r2_{pid}", help="You're not alone",
                          on_click=circle_toggle_like, args=(pid, None, None, R2), use_container_width=True)
            with col_r3:
                liked = f"{pid}|None|None|{R3}" in st.session_state.circle_liked
                st.button(f"🔥 {reactions.get(R3, 0)}", key=f"r3_{pid}", help="We got this",
                          on_click=circle_toggle_like, args=(pid, None, None, R3), use_container_width=True)
            with col_cm:
                st.button(f"💬 {total_comments}", key=f"cm_{pid}", help="Show / hide comments",
                          on_click=circle_toggle_comments, args=(pid,), use_container_width=True)
            with col_dm:
                if st.button("🤝 Support", key=f"dm_{pid}", help="Send a private encouraging note", use_container_width=True):
                    st.session_state.circle_selected_dm_post = pid
                    st.rerun()

            if pid in st.session_state.circle_open_comments:
                st.markdown("---")
                for comment in comments:
                    cid = comment["id"]
                    st.markdown(circle_comment_html(comment), unsafe_allow_html=True)
                    cl1, cl2, _sp = st.columns([1, 1, 4])
                    with cl1:
                        c_liked = f"{pid}|{cid}|None|None" in st.session_state.circle_liked
                        st.button(f"{'♥' if c_liked else '♡'} {comment.get('likes', 0)}", key=f"cl_{cid}",
                                  on_click=circle_toggle_like, args=(pid, cid, None, None), use_container_width=True)
                    with cl2:
                        st.button("↩ Reply", key=f"crp_{cid}", on_click=circle_start_reply, args=(pid, cid), use_container_width=True)

                    for reply in comment.get("replies", []):
                        rid = reply["id"]
                        st.markdown(circle_comment_html(reply, indent=True), unsafe_allow_html=True)
                        rl1, _rsp = st.columns([1, 5])
                        with rl1:
                            r_liked = f"{pid}|{cid}|{rid}|None" in st.session_state.circle_liked
                            st.button(f"{'♥' if r_liked else '♡'} {reply.get('likes', 0)}", key=f"rl_{rid}",
                                      on_click=circle_toggle_like, args=(pid, cid, rid, None), use_container_width=True)

                    if st.session_state.circle_reply_to == f"{pid}|{cid}":
                        rin, rbtn = st.columns([4, 1], vertical_alignment="bottom")
                        with rin:
                            st.text_input("Reply", key=f"reply_in_{cid}", placeholder="Write a kind reply...", label_visibility="collapsed")
                        with rbtn:
                            st.button("Send", key=f"reply_send_{cid}", on_click=circle_add_reply, args=(pid, cid), use_container_width=True)

                if not comments:
                    st.caption("No comments yet. Be the first to say something kind 🌿")

                cin, cbtn = st.columns([4, 1], vertical_alignment="bottom")
                with cin:
                    st.text_input("Add a comment", key=f"cmt_in_{pid}", placeholder="Write a supportive comment...", label_visibility="collapsed")
                with cbtn:
                    st.button("Post", key=f"cmt_send_{pid}", on_click=circle_add_comment, args=(pid,), use_container_width=True)

    if st.session_state.circle_selected_dm_post:
        st.markdown("---")
        st.markdown("### 🔒 Send Private Support")
        dm_input = st.text_input("Encouraging message:")
        if st.button("Send 🚀"):
            st.success("Encouragement sent anonymously!")
            st.session_state.circle_selected_dm_post = None
            st.rerun()


elif st.session_state.page == "Profile":
    st.markdown('<div class="brand-small">YOUR SPACE</div>', unsafe_allow_html=True)
    st.title("🌿 Profile & Analytics")

    with st.container():
        st.markdown("### 👤 Student Profile")
        st.write(f"**Name:** {st.session_state.student_name}")
        st.write(f"**Class / Grade:** {st.session_state.student_class}")
        st.write(f"**Student ID:** `{st.session_state.student_id}`")

    with st.container():
        st.markdown("### 🤝 Trusted Adult Contact")
        if st.session_state.trusted_adult_info:
            adult = st.session_state.trusted_adult_info
            st.write(f"**Name:** {adult.get('Name')}")
            st.write(f"**Relationship:** {adult.get('Relationship')}")
            st.write(f"**Phone:** {adult.get('Contact')}")
        else:
            st.info("No trusted adult added yet. Add one below:")
            with st.form("add_adult_profile_form"):
                p_name = st.text_input("Adult's Name", placeholder="e.g. Ms. Sarah")
                p_rel = st.text_input("Relationship", placeholder="e.g. School Counsellor")
                p_contact = st.text_input("Phone Number", placeholder="+1 555-0192")
                if st.form_submit_button("Save Trusted Adult"):
                    if p_contact.strip():
                        adult_record = {
                            "Adult_ID": f"AD-{random.randint(1000, 9999)}",
                            "Student_ID": st.session_state.student_id,
                            "Name": p_name.strip() if p_name.strip() else "Trusted Support",
                            "Relationship": p_rel.strip() if p_rel.strip() else "Support",
                            "Contact_Type": "Phone",
                            "Contact": p_contact.strip(),
                        }
                        st.session_state.trusted_adult_info = adult_record
                        append_to_excel("09_Trusted_Adults", adult_record)
                        st.success("Saved!")
                        st.rerun()

    with st.container():
        st.markdown("### 🩺 Emergency Helplines & Support")
        with st.expander("📞 View National Helplines"):
            st.markdown("• **Childline Support:** Call `1098` (Free 24/7)")
            st.markdown("• **Mental Health Helpline:** Call `14416` or `1800-891-4416`'")
            st.markdown("• [Find Student Counsellors Nearby 🔗](https://www.google.com/maps/search/student+counsellors+near+me/)")

    with st.container():
        st.markdown("### 📅 Monthly Mood Calendar")
        now = datetime.now()
        cal = calendar.monthcalendar(now.year, now.month)
        
        date_emoji_map = {}
        for entry in st.session_state.mood_history:
            date_str = entry.get("date")
            emoji = entry.get("emoji", "😊")
            if date_str:
                date_emoji_map[date_str] = emoji

        cal_html = '<table class="calendar-table"><thead><tr><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th><th>Sun</th></tr></thead><tbody>'
        for week in cal:
            cal_html += "<tr>"
            for day in week:
                if day == 0:
                    cal_html += "<td></td>"
                else:
                    day_formatted = f"{now.year}-{now.month:02d}-{day:02d}"
                    punched_emoji = date_emoji_map.get(day_formatted, "")
                    cal_html += f'<td><div style="font-size:10px; color:var(--text-muted);">{day}</div><div>{punched_emoji}</div></td>'
            cal_html += "</tr>"
        cal_html += "</tbody></table>"
        st.markdown(cal_html, unsafe_allow_html=True)

    with st.container():
        st.markdown("### 📊 Mood Analytics")
        if st.session_state.mood_history:
            df_moods = pd.DataFrame(st.session_state.mood_history)
            st.markdown("#### Mood Check-in Breakdown")
            try:
                import altair as alt
                _mood_counts = df_moods["mood"].value_counts().reset_index()
                _mood_counts.columns = ["mood", "count"]
                _dark = st.session_state.theme_mode == "dark"
                _fg = "#ECEFED" if _dark else "#2C3531"
                _grid = "#2D3A34" if _dark else "#EAE5DE"
                _bar = "#8EAFA0" if _dark else "#6E8B74"
                _mood_chart = (
                    alt.Chart(_mood_counts)
                    .mark_bar(color=_bar, cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
                    .encode(
                        x=alt.X("mood:N", sort="-y", title=None, axis=alt.Axis(labelAngle=0)),
                        y=alt.Y("count:Q", title=None, axis=alt.Axis(tickMinStep=1)),
                        tooltip=["mood", "count"],
                    )
                    .properties(height=260)
                    .configure(background="transparent")
                    .configure_axis(labelColor=_fg, titleColor=_fg, gridColor=_grid, domainColor=_grid, tickColor=_grid)
                    .configure_view(strokeWidth=0)
                )
                st.altair_chart(_mood_chart, use_container_width=True, theme=None)
            except Exception:
                st.bar_chart(df_moods["mood"].value_counts())
        else:
            st.info("Check in your mood on the Home tab to unlock analytics!")


# ============================================================
# 12. NAVIGATION BAR (AT VERY END)
# ============================================================

st.markdown("<br><br><br>", unsafe_allow_html=True)
nav1, nav2, nav3, nav4, nav5, nav6, nav7 = st.columns(7)

with nav1:
    if st.button("⌂\nHome", key="nav_h", use_container_width=True):
        go_to("Home")
        st.rerun()
with nav2:
    if st.button("💬\nChat", key="nav_c", use_container_width=True):
        go_to("Chat")
        st.rerun()
with nav3:
    if st.button("🌿\nReset", key="nav_a", use_container_width=True):
        go_to("Activities")
        st.rerun()
with nav4:
    if st.button("✨\nExplore", key="nav_e", use_container_width=True):
        go_to("Explore")
        st.rerun()
with nav5:
    if st.button("🌎\nCircle", key="nav_circle", use_container_width=True):
        go_to("Circle")
        st.rerun()
with nav6:
    if st.button("🧠\nDump", key="nav_dump", use_container_width=True):
        go_to("Brain Dump")
        st.rerun()
with nav7:
    if st.button("○\nProfile", key="nav_p", use_container_width=True):
        go_to("Profile")
        st.rerun()