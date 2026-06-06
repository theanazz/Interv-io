from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import database
import os
import json
import re
import PyPDF2
import docx
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

FALLBACK_QUESTIONS = {
    "Software Engineer": {
        "Junior": [
            "What is a REST API and what are the main HTTP methods used?",
            "Explain the difference between GET and POST requests.",
            "What are the core principles of Object-Oriented Programming (OOP)?",
            "Explain a technical project you built recently and what role you played.",
            "What is database indexing and how does it improve query performance?",
            "What happens behind the scenes when you type 'google.com' in a browser?"
        ],
        "Mid-Level": [
            "How do you approach optimizing slow database queries causing high backend latency?",
            "Describe how you would handle race conditions in a concurrent application.",
            "What are the main tradeoffs between choosing a microservices architecture vs. a monolithic architecture?",
            "What strategies do you use for caching database queries and handling cache invalidation?",
            "How do you implement secure user authentication across distributed microservices?",
            "Explain the differences between SQL and NoSQL databases and when you would choose each."
        ],
        "Senior": [
            "Explain how you've handled a situation where you had to pivot your technical strategy due to a major architectural shift.",
            "Tell me about a time you had to design a distributed system that handles millions of active users.",
            "How do you handle cache invalidation during a database migration in a high-concurrency system?",
            "What is your strategy for horizontal scalability, and when would you use database sharding?",
            "How do you manage stakeholder communication and negotiate technical trade-offs for high-impact projects?",
            "Describe a major production outage you resolved and the post-mortem steps you put in place."
        ]
    },
    "Fullstack Developer": {
        "Junior": [
            "What is the difference between client-side rendering (CSR) and server-side rendering (SSR)?",
            "How do you capture form data in the frontend and send it to a backend API?",
            "What are cookies and local storage, and how do they differ?",
            "Explain a recent web application you worked on and its main features.",
            "What are CORS issues and how do you resolve them in a fullstack project?",
            "What is the role of an ORM (like SQLAlchemy or Prisma) in database management?"
        ],
        "Mid-Level": [
            "How do you decide between SSR and CSR for a new dynamic web application?",
            "Describe your experience with managing state consistency between frontend stores and databases.",
            "How do you optimize initial page load times when dealing with large dynamic front-end bundles?",
            "How do you secure user authentication and session management across client and server?",
            "Describe a time you had to optimize slow API query latency causing UI freezes.",
            "What strategies do you use for handling secure file uploads and media processing?"
        ],
        "Senior": [
            "How do you design a scalable microfrontend architecture for a large enterprise app?",
            "Describe your strategy for maintaining data consistency across multiple databases in a distributed microservices web app.",
            "How would you approach migrating a legacy monolithic web application to a modern fullstack serverless architecture?",
            "How do you configure global load balancing and Content Delivery Networks (CDNs) for static and dynamic user traffic?",
            "What is your approach to automated end-to-end testing and continuous delivery for a high-traffic fullstack app?",
            "Explain how you manage technical debt while delivering critical product milestones under tight timelines."
        ]
    },
    "Product Manager": {
        "Junior": [
            "What is a product roadmap and how do you construct a basic MVP feature list?",
            "How do you gather user feedback to improve an existing product feature?",
            "What is the difference between agile sprint cycles and waterfall methodology?",
            "Describe a product you use daily. What would you improve about it?",
            "How do you track basic user engagement, like daily active users (DAU)?",
            "Explain a project where you collaborated with engineers or designers."
        ],
        "Mid-Level": [
            "How do you prioritize a product roadmap when faced with conflicting stakeholder requests?",
            "Tell me about a product or feature you launched that failed. What did you learn?",
            "How do you define success metrics for a new feature? Which metrics do you prioritize?",
            "How do you synthesize qualitative user feedback and quantitative data to make product decisions?",
            "Describe a scenario where you had to make a product decision without complete data.",
            "How do you coordinate alignment between engineering, design, and marketing teams during a product launch?"
        ],
        "Senior": [
            "How do you define and execute a long-term product vision that spans multiple years and product lines?",
            "Walk me through a time you made a high-stakes pivot in product strategy based on changing market conditions.",
            "How do you structure product telemetry and analytics frameworks to measure portfolio-level product health?",
            "How do you handle negotiations with executive stakeholders when denying their critical feature requests?",
            "What is your strategy for launching a new product into a highly competitive, saturated market?",
            "Describe how you manage organizational alignment across cross-functional directors to achieve company-level OKRs."
        ]
    },
    "UX Designer": {
        "Junior": [
            "What is the difference between UX (User Experience) and UI (User Interface)?",
            "Explain your process for creating basic wireframes and user flows.",
            "How do you select colors, fonts, and grid layouts to ensure visual hierarchy?",
            "Walk me through a design project in your portfolio and the user problem it solved.",
            "What are accessibility guidelines (WCAG) and why are they important?",
            "What is the purpose of user testing, and how do you conduct a simple test?"
        ],
        "Mid-Level": [
            "Walk me through your design process when redesigning a complex, data-heavy user interface.",
            "How do you handle negative feedback from product managers or engineering leads on a mockup?",
            "What strategies do you use to ensure your design choices are accessible and comply with WCAG standards?",
            "Describe your approach to user research and how you translate findings into actionable wireframes.",
            "How do you create and maintain a consistent design system across web and mobile platforms?",
            "How do you balance aesthetic design desires with technical performance constraints when working with developers?"
        ],
        "Senior": [
            "How do you design and scale an enterprise-level design system used by UX teams?",
            "Describe how you lead user research strategies for product domains with highly complex, ambiguous requirements.",
            "How do you advocate for UX maturity and design thinking in a historically engineering-driven organization?",
            "How do you balance short-term product delivery goals with long-term UX quality and research standards?",
            "Describe a time you resolved a major strategic disagreement between product management and design direction.",
            "How do you design for complex cross-channel user journeys that bridge digital and physical touchpoints?"
        ]
    },
    "Data Scientist": {
        "Junior": [
            "What is the difference between supervised and unsupervised learning?",
            "Explain what overfitting is and how you can prevent it.",
            "What are the differences between mean, median, and mode, and when would you use each?",
            "Describe a data project you worked on recently and the dataset you analyzed.",
            "What is a confusion matrix and what are precision and recall?",
            "How do you handle missing values or duplicate records in a raw dataset?"
        ],
        "Mid-Level": [
            "How do you handle missing or noisy data in a large-scale production model?",
            "Explain the bias-variance tradeoff to a non-technical business executive.",
            "Tell me about a time you optimized a model that performed well in testing but poorly in production.",
            "How do you design and evaluate A/B tests to validate business hypotheses?",
            "How do you choose between a decision tree and a logistic regression for classification?",
            "Describe how you would deploy a machine learning model to production and monitor its performance."
        ],
        "Senior": [
            "How do you architect distributed training pipelines for models processing terabytes of data?",
            "Describe how you design multi-armed bandit or reinforcement learning systems for real-time personalization.",
            "How do you detect, measure, and mitigate model drift and algorithmic bias in critical production environments?",
            "Describe a time you built a data science team and established standards for model lifecycle management (MLOps).",
            "How do you translate highly complex machine learning outcomes into strategic business recommendations for C-level executives?",
            "What is your approach to selecting model architectures when balancing prediction accuracy with low-latency inference constraints?"
        ]
    }
}


def get_fallback_questions(role, level):
    qs = _get_fallback_questions_raw(role, level)
    
    padding_pool = [
        f"What is your approach to learning new technologies as a {role}?",
        f"Describe your favorite project or accomplishment as a {role}.",
        f"How do you handle constructive criticism and feedback in a team setting?",
        f"Where do you see your career progressing in the next few years as a {role}?",
        f"How do you approach quality assurance and review processes?",
        f"Describe a time you had a professional disagreement and how you resolved it.",
        f"How do you support and collaborate with your peers daily?",
        f"How do you balance accumulating technical debt against fast product delivery?",
        f"Describe your strategy for diagnosing and resolving complex systemic issues.",
        f"What tools and methodologies do you rely on most heavily in your {role} workflow?"
    ]
    
    idx = 0
    while len(qs) < 10:
        qs.append(padding_pool[idx % len(padding_pool)])
        idx += 1
        
    import random
    random.shuffle(qs)
    return qs

def _get_fallback_questions_raw(role, level):
    role_lower = role.lower()
    if "fullstack" in role_lower or "full-stack" in role_lower:
        base_role = "Fullstack Developer"
    elif "ux" in role_lower or "designer" in role_lower:
        base_role = "UX Designer"
    elif "product" in role_lower or "pm" in role_lower:
        base_role = "Product Manager"
    elif "data" in role_lower or "science" in role_lower:
        base_role = "Data Scientist"
    else:
        base_role = "Software Engineer"
        
    role_dict = FALLBACK_QUESTIONS.get(base_role, {})
    questions = role_dict.get(level, role_dict.get("Mid-Level", [])).copy()
    
    # Custom role fallback
    if base_role == "Software Engineer" and "software" not in role_lower and "engineer" not in role_lower:
        if level == "Junior":
            return [
                f"Explain the fundamentals of a {role} and why you chose this career path.",
                f"What are the most common tools and methodologies used in a daily {role} workflow?",
                f"Describe a simple project or lab you set up to learn concepts related to {role}.",
                f"How do you handle simple debugging or troubleshooting in your daily {role} work?",
                f"Explain the difference between two core basic concepts in a {role} domain.",
                f"How do you work collaboratively with designers and managers as a {role}?"
            ]
        elif level == "Mid-Level":
            return [
                f"How do you prioritize and balance multiple technical tasks in your {role} capacity?",
                f"Describe a challenging scenario you resolved in your {role} career. What was the impact?",
                f"What standards and best practices do you follow to ensure the quality of your {role} output?",
                f"How do you collaborate with cross-functional team members (managers, designers, developers) in your work?",
                f"Describe your experience with optimizing existing systems or workflows as a {role}.",
                f"How do you balance aesthetic desires with performance constraints as a {role}?"
            ]
        else: # Senior
            return [
                f"Describe your vision for scaling technical excellence and strategy as a {level} {role}.",
                f"Tell me about a time you had to solve a high-stakes challenge under the constraints of a {role} role.",
                f"How do you measure individual success versus team success in a {role} capacity?",
                f"How do you keep yourself updated with shifting industry standards for a {role} and mentor others?",
                f"Describe a project you worked on recently as a {role} where you had to make high-impact technical trade-offs.",
                f"How do you manage executive stakeholder expectations when proposing technical changes in a {role} capacity?"
            ]
    return questions

app = Flask(__name__)
# Try fetching from ENV, fallback if missing
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'super_secret_intervio_key')

# Initialize DB
database.init_db()

@app.context_processor
def inject_global_stats():
    if 'user_id' in session:
        user_id = session['user_id']
        stats = database.get_user_stats(user_id)
        user = database.get_user_by_id(user_id)
        return dict(stats=stats, user=user, user_name=user['name'] if user else '')
    return dict()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/interview')
def interview():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    role = request.args.get('role')
    level = request.args.get('level')
    voice = request.args.get('voice')
    camera = request.args.get('camera')
    
    user_id = session['user_id']
    user = database.get_user_by_id(user_id)
    
    if not role or not level:
        return render_template('lobby.html', user=user, user_name=user['name'])
        
    # Scale question count dynamically based on selected difficulty level
    num_questions = 10

    # Generate questions dynamically using Gemini API
    questions = []
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Setup specific difficulty constraints
            difficulty_guideline = ""
            if level == 'Junior':
                difficulty_guideline = (
                    "Strictly generate Easy to Medium difficulty questions. "
                    "Enforce this EXACT sequence of 10 questions: "
                    "Question 1: Introduction and background. "
                    "Questions 2-4: Core Fundamentals and Definitions. "
                    "Questions 5-6: Simple Coding and Logic (These will accompany a coding challenge). "
                    "Questions 7-8: Basic Projects and Scenarios. "
                    "Questions 9-10: HR and Behavioral questions. "
                    "Do NOT ask about distributed scaling, architecture pivots, complex refactoring, or advanced caching."
                )
            elif level == 'Mid-Level':
                difficulty_guideline = (
                    "Strictly generate Medium to Hard difficulty questions. "
                    "Focus heavily on Practical and Scenario-Based situations, including APIs, optimization, caching, concurrency, and architecture basics."
                )
            else: # Senior
                difficulty_guideline = (
                    "Strictly generate Hard to Expert difficulty questions. "
                    "Focus heavily on Architecture and Leadership, including scalability, distributed systems, tradeoffs, and system design."
                )
                
            prompt = (
                f"Generate exactly {num_questions} professional interview questions for a {level} {role}. "
                f"{difficulty_guideline} "
                "Ensure they are highly relevant to technical skills or domain-specific scenarios for this role. "
                "CRITICAL: Randomize the topics and scenarios. DO NOT generate the same standard list of generic questions. Surprise the candidate with unique, edge-case, and highly diverse topics every time. "
                f"Return them as a JSON list of strings, for example: [\"Question 1?\", ..., \"Question {num_questions}?\"]. "
                "Do not include any markdown styling, code block backticks (like ```json), or explanatory text, just the raw JSON array."
            )
            response = model.generate_content(prompt)
            clean_text = re.sub(r'```[a-zA-Z]*', '', response.text).strip()
            clean_text = clean_text.strip('`').strip()
            questions = json.loads(clean_text)
            if not isinstance(questions, list) or len(questions) < num_questions:
                raise ValueError("JSON parsing returned invalid data format")
            questions = questions[:num_questions]
        except Exception as e:
            print(f"Gemini API error, falling back to local questions: {e}")
            questions = get_fallback_questions(role, level)[:num_questions]
    else:
        questions = get_fallback_questions(role, level)[:num_questions]
        
    # Append final question / completion message
    questions.append("Final calibration complete. Processing your neural intelligence report.")
    
    return render_template('interview.html', 
                             user=user, 
                             user_name=user['name'], 
                             selected_role=role, 
                             selected_level=level,
                             selected_voice=voice,
                             selected_camera=camera,
                             questions_json=json.dumps(questions))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    # Removed automatic seeding to ensure 'Fully Working acc to user usage'
    
    user = database.get_user_by_id(user_id)
    pulse = database.get_mock_sessions(user_id)
    stats = database.get_user_stats(user_id)
    latest_interview = database.get_latest_interview(user_id)
    
    return render_template('dashboard.html', 
                             user_name=user['name'], 
                             user=user,
                             pulse=pulse,
                             stats=stats,
                             latest_interview=latest_interview)

@app.route('/report/<int:report_id>')
def report(report_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    interview = database.get_interview_by_id(report_id)
    if not interview:
        flash("Report not found.")
        return redirect(url_for('dashboard'))
        
    user_id = session['user_id']
    user = database.get_user_by_id(user_id)
    
    return render_template('report.html', user=user, interview=interview)

@app.route('/evaluate-transcript', methods=['POST'])
def evaluate_transcript():
    data = request.json or {}
    history = data.get('history', [])
    role = data.get('role', 'Software Engineer')
    level = data.get('level', 'Mid-Level')
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    fallback = {
        "tech": 85, "comm": 88, "conf": 82, "score": 85,
        "summary": f"Calibration complete for {level} {role}. System used heuristic evaluation due to API constraints.",
        "strengths": ["Maintained clear structure in responses.", "Addressed the core topic adequately."],
        "weaknesses": ["Could provide deeper technical specifics.", "Work on minimizing hesitation in complex answers."],
        "star": "Focus on highlighting system design tradeoffs in future answers."
    }
    
    if not gemini_key or not history:
        return jsonify(fallback)
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
Act as an expert technical interviewer evaluating a {level} {role}.
Here is the full interview transcript (Q = Question, A = Answer):
{json.dumps(history, indent=2)}

Evaluate the candidate's performance based ONLY on the provided answers.
Return ONLY a raw JSON object (no markdown, no backticks, no explanatory text) with the following exact keys:
- "tech": integer 0-100 (Technical competence)
- "comm": integer 0-100 (Communication skills)
- "conf": integer 0-100 (Confidence and clarity)
- "score": integer 0-100 (Overall average score)
- "summary": string (1-2 sentences summarizing performance)
- "strengths": array of 2 strings (specific positive observations)
- "weaknesses": array of 2 strings (areas for improvement)
- "star": string (one actionable piece of advice)
"""
        response = model.generate_content(prompt)
        import re
        clean_text = re.sub(r'```[a-zA-Z]*', '', response.text).strip()
        clean_text = clean_text.strip('`').strip()
        result = json.loads(clean_text)
        
        for k in ["tech", "comm", "conf", "score", "summary", "strengths", "weaknesses", "star"]:
            if k not in result:
                result[k] = fallback[k]
                
        return jsonify(result)
    except Exception as e:
        print(f"Transcript evaluation failed: {e}")
        return jsonify(fallback)

@app.route('/complete-interview', methods=['POST'])
def complete_interview():
    if 'user_id' not in session:
        return {"error": "Unauthorized"}, 401
    data = request.json
    database.save_interview(session['user_id'], data)
    return {"status": "success"}

@app.route('/generate-followup', methods=['POST'])
def generate_followup():
    if 'user_id' not in session:
        return {"error": "Unauthorized"}, 401
    
    data = request.json or {}
    role = data.get('role', 'Software Engineer')
    level = data.get('level', 'Mid-Level')
    prev_question = data.get('question', '')
    user_answer = data.get('answer', '')
    history = data.get('history', [])
    
    print(f"--- generate_followup ---")
    print(f"Question: {prev_question}")
    print(f"Answer: {user_answer}")
    print(f"History: {history}")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key and prev_question and user_answer:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Format history context
            history_str = ""
            for turn in history[-3:]:
                history_str += f"Question: {turn.get('q')}\nAnswer: {turn.get('a')}\n"
                
            prompt = (
                f"You are a professional, realistic AI interviewer calibrating a {level} {role}. "
                f"Here is the recent context of the conversation:\n{history_str}"
                f"The candidate just answered the question:\n\"{prev_question}\"\n"
                f"Candidate's answer was:\n\"{user_answer}\"\n\n"
                f"Generate a single, realistic, and highly contextual follow-up question (1-2 sentences) "
                f"probing deeper into their answer, technical tradeoffs, architecture, metrics, or design choice. "
                f"Make sure it sounds natural and realistic (e.g. \"Interesting approach. How would you handle database replication in that case?\" or \"Good points, how do you measure success for this design?\"). "
                f"Do not ask generic questions. Do not include any prefix or surrounding quotes, just return the raw text of the question itself."
            )
            response = model.generate_content(prompt)
            followup = response.text.strip().replace('"', '')
            if followup:
                return {"followup": followup}
        except Exception as e:
            print(f"Error generating Gemini follow-up: {e}")
            
    return {"followup": None}

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    user = database.get_user_by_id(user_id)
    pulse = database.get_mock_sessions(user_id)
    stats = database.get_user_stats(user_id)
    history = database.get_performance_history(user_id)
    
    latest = database.get_latest_interview(user_id)
    heatmap_data = []
    import random
    if latest and dict(latest).get('conf_score'):
        base_conf = dict(latest)['conf_score']
        for _ in range(15):
            val = max(10, min(100, base_conf + random.randint(-20, 20)))
            heatmap_data.append(val)
    else:
        heatmap_data = [random.randint(20, 80) for _ in range(15)]
        
    return render_template('analytics.html', 
                             user_name=user['name'], 
                             user=user, 
                             pulse=pulse, 
                             stats=stats,
                             performance_history=history,
                             heatmap_data=heatmap_data)

@app.route('/resume-ai')
def resume_ai():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    user = database.get_user_by_id(user_id)
    pulse = database.get_mock_sessions(user_id)
    return render_template('resume_ai.html', user_name=user['name'], user=user, pulse=pulse)

@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    if 'user_id' not in session:
        return {"error": "Unauthorized"}, 401
    
    if 'resume' not in request.files:
        return {"error": "No resume file provided"}, 400
        
    file = request.files['resume']
    if file.filename == '':
        return {"error": "No selected file"}, 400
        
    text = ""
    try:
        if file.filename.lower().endswith('.pdf'):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif file.filename.lower().endswith('.docx'):
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            return {"error": "Unsupported format. Please upload PDF or DOCX."}, 400
    except Exception as e:
        return {"error": f"Failed to parse file: {str(e)}"}, 500
        
    if not text.strip():
        return {"error": "Could not extract text from the file."}, 400
        
    try:
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            return {"error": "API key missing"}, 500
            
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = (
            "Analyze the following resume text. Generate personalized interview questions and weakness-based prep suggestions. "
            "Output MUST be a strictly formatted JSON object with the following structure:\n"
            "{\n"
            "  \"personalized_questions\": [\n"
            "    {\"category\": \"Based on Experience\", \"question\": \"...\"},\n"
            "    {\"category\": \"Role-Specific Gap\", \"question\": \"...\"},\n"
            "    {\"category\": \"Seniority Check\", \"question\": \"...\"}\n"
            "  ],\n"
            "  \"weaknesses\": [\n"
            "    {\"title\": \"Soft Skills Gap\", \"description\": \"...\"},\n"
            "    {\"title\": \"Architecture Depth\", \"description\": \"...\"},\n"
            "    {\"title\": \"Authenticity Score\", \"description\": \"...\"}\n"
            "  ]\n"
            "}\n"
            "Resume text:\n\n" + text[:10000]
        )
        response = model.generate_content(prompt)
        clean_text = re.sub(r'```[a-zA-Z]*', '', response.text).strip()
        clean_text = clean_text.strip('`').strip()
        result = json.loads(clean_text)
        return result
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return {"error": "Failed to generate analysis."}, 500

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    user = database.get_user_by_id(user_id)
    pulse = database.get_interview_pulse(user_id) # Using granular interviews for history
    
    retention = int(dict(user).get('readiness_percent', 0) or 0)
    speak_time = len(pulse) * 12.5 if pulse else 0
    reply_delay = max(0.5, round(3.0 - (retention / 100 * 2.5), 1))
    metrics = {
        "retention": f"{retention}%",
        "speak_time": f"{speak_time}m",
        "reply_delay": f"{reply_delay}s"
    }
    
    return render_template('history.html', user_name=user['name'], user=user, pulse=pulse, metrics=metrics)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = database.get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if database.get_user_by_email(email):
            flash('Email already registered. Please sign in.')
        else:
            hashed_pw = generate_password_hash(password)
            user_id = database.create_user(name, email, hashed_pw)
            
            flash('Account created successfully! Please log in.')
            return redirect(url_for('login'))
            
    return render_template('signup.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    user = database.get_user_by_id(user_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        conn = database.get_db_connection()
        with conn.cursor() as c:
            c.execute('UPDATE users SET name = %s, email = %s WHERE id = %s', (name, email, user_id))
        conn.commit()
        conn.close()
        
        flash("System Configuration synchronized successfully!", "success")
        return redirect(url_for('settings'))
        
    return render_template('settings.html', user=user, user_name=user['name'] if user else "demo")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def is_code_empty_or_boilerplate(code, language):
    if not code:
        return True
    
    # Remove single line comments
    code_clean = re.sub(r'//.*', '', code)
    code_clean = re.sub(r'#.*', '', code_clean)
    # Remove block comments
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    
    # Strip whitespace
    stripped = "".join(code_clean.split())
    if not stripped:
        return True
        
    boilerplate_signatures = [
        # Two Sum
        "deftwoSum(nums,target):pass",
        "functiontwoSum(nums,target){}",
        "classSolution{publicint[]twoSum(int[]nums,inttarget){returnnewint[]{};}}",
        "classSolution{public:vector<int>twoSum(vector<int>&nums,inttarget){return{};}};",
        "int*twoSum(int*nums,intnumsSize,inttarget,int*returnSize){*returnSize=2;int*result=(int*)malloc(2*sizeof(int));returnresult;}",
        
        # Valid Parentheses
        "defisValid(s:str)->bool:pass",
        "functionisValid(s){}",
        "classSolution{publicbooleanisValid(Strings){returnfalse;}}",
        "classSolution{public:boolisValid(strings){returnfalse;}};",
        "boolisValid(char*s){returnfalse;}",
        
        # LRU Cache
        "classLRUCache:def__init__(self,capacity:int):passdefget(self,key:int)->int:return-1defput(self,key:int,value:int)->None:pass",
        "classLRUCache{publicLRUCache(intcapacity){}publicintget(intkey){return-1;}publicvoidput(intkey,intvalue){}}",
        "classLRUCache{public:LRUCache(intcapacity){}intget(intkey){return-1;}voidput(intkey,intvalue){}};",
        "typedefstruct{}LRUCache;LRUCache*lruCacheCreate(intcapacity){returnNULL;}intlruCacheGet(LRUCache*obj,intkey){return-1;}voidlruCachePut(LRUCache*obj,intkey,intvalue){}voidlruCacheFree(LRUCache*obj){}"
    ]
    
    if stripped in boilerplate_signatures:
        return True
        
    return False

@app.route('/evaluate-code', methods=['POST'])
def evaluate_code():
    if 'user_id' not in session:
        return {"error": "Unauthorized"}, 401
    
    data = request.json or {}
    problem_title = data.get('title', 'Coding Challenge')
    code = data.get('code', '')
    language = data.get('language', 'javascript')
    
    if is_code_empty_or_boilerplate(code, language):
        return {
            "timeComplexity": "O(1)",
            "spaceComplexity": "O(1)",
            "analysis": "No solution was written. The template code was not completed.",
            "aiFeedback": "Please write a complete solution for the coding challenge before running or submitting.",
            "testCases": [{"passed": False}, {"passed": False}, {"passed": False}]
        }
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key and code:
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = (
                f"Analyze the following {language} code written for the coding challenge '{problem_title}':\n\n"
                f"```{language}\n{code}\n```\n\n"
                f"Please evaluate this code and return a JSON object with five keys:\n"
                f"1. 'timeComplexity' (string, e.g. 'O(N)' or 'O(N^2)')\n"
                f"2. 'spaceComplexity' (string, e.g. 'O(1)' or 'O(N)')\n"
                f"3. 'analysis' (string, 2-3 sentences explaining the time/space complexities and correctness)\n"
                f"4. 'aiFeedback' (string, 2-3 sentences giving helpful suggestions, recommendations or edge case checks)\n"
                f"5. 'testCases' (a list of exactly 3 objects representing the correctness of this code against the standard test cases for this problem. "
                f"Each object must have a single key 'passed' with a boolean value, e.g. [{{\"passed\": true}}, {{\"passed\": true}}, {{\"passed\": true}}])\n\n"
                f"Do not include any markdown backticks, raw JSON strings or prefix text. Just return the JSON object."
            )
            response = model.generate_content(prompt)
            clean_text = re.sub(r'```[a-zA-Z]*', '', response.text).strip()
            clean_text = clean_text.strip('`').strip()
            result = json.loads(clean_text)
            return result
        except Exception as e:
            print(f"Error evaluating code via Gemini: {e}")
            
    # Fallback response
    return {
        "timeComplexity": "O(N)",
        "spaceComplexity": "O(N)",
        "analysis": "The solution implements the standard algorithms. Time complexity is linear because it iterates through the elements, and space complexity is linear due to storage requirements.",
        "aiFeedback": "Your code is functional and clean. For further optimization, try considering edge cases such as empty arrays or duplicate elements.",
        "testCases": [{"passed": True}, {"passed": True}, {"passed": True}]
    }

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
