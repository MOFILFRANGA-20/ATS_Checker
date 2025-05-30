import os
import google.generativeai as genai
from flask import Flask, render_template, request
from pdfminer.high_level import extract_text
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
genai.configure(api_key=os.getenv("AIzaSyCgoJDCsjo7u4ZDR4XqGMsYAg8rnh350x8"))


def extract_resume_text(pdf_path):
    return extract_text(pdf_path)


def compare_keywords(resume_text, job_description):
    resume_words = set(resume_text.lower().split())
    job_words = set(job_description.lower().split())
    match = resume_words.intersection(job_words)
    score = int((len(match) / len(job_words)) * 100)
    return score


def get_suggestions_gemini(resume_text, job_description):
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""
You are an ATS system. A user uploaded a resume. Compare it with this job description.
Give short bullet point suggestions to improve the resume for better matching.

Resume Text:
{resume_text}

Job Description:
{job_description}

Only give 3 to 5 bullet points.
"""
    response = model.generate_content(prompt)
    return response.text.split('\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def result():
    resume = request.files['resume']
    job_desc = request.form['job_description']

    pdf_path = 'temp_resume.pdf'
    resume.save(pdf_path)

    resume_text = extract_resume_text(pdf_path)
    score = compare_keywords(resume_text, job_desc)
    suggestions = get_suggestions_gemini(resume_text, job_desc)

    os.remove(pdf_path)
    return render_template('result.html', score=score, suggestions=suggestions)


if __name__ == '__main__':
    app.run(debug=True)
