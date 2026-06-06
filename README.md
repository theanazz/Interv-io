# ⚡ interv.io

A premium AI-powered technical and behavioral interview simulation platform. Built with a cyberpunk, dark-mode design architecture, it features real-time voice synthesis, algorithmic problem generation, and deep AI behavioral analytics.

## 🌟 Core Features

- **🎙️ Immersive AI Interviews**: Real-time voice-activated technical and behavioral calibration sessions using an advanced Neural Hub layout.
- **💻 Dynamic Coding Workspace**: Integrated Monaco editor with "Terminal Mode" typing effects. Coding challenges are randomized dynamically (including FizzBuzz, Two Sum, Contains Duplicate, Valid Palindrome).
- **📊 Performance Intelligence**: Deep behavioral analytics tracking technical accuracy, communication clarity, and confidence. Features a fully interactive graph with toggleable Technical/Communication filters.
- **📄 Export & Share**: Native integration for exporting beautiful, dark-mode PDFs of your past performances or sharing secure links with mentors.
- **⚙️ System Configuration**: A fully interactive backend Settings module for dynamically updating user profiles and parameters.
- **🔔 Interactive Notifications**: Smart top-bar notifications with one-click clear, individual dismissal, and auto-hiding badges.
- **🌌 Full-Screen Focus**: The UI intelligently strips away sidebars and navigation panels during active simulations to enforce an edge-to-edge immersive experience.

## 🛠️ Tech Stack

- **Backend**: Python, Flask, SQLite3, Werkzeug
- **Frontend**: HTML5, Vanilla JavaScript, Tailwind CSS, Jinja2
- **Integrations**: Chart.js for data visualization, Monaco Editor for real-time IDE environment.

## 🚀 Installation & Setup

Follow these instructions to run the interv.io platform on your local machine:

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/interv.io.git
   cd interv.io
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**
   The application uses SQLite3. The database will automatically initialize when you first run the server, but ensure you have write permissions in the root directory.

5. **Start the Application**
   ```bash
   python app.py
   ```
   The platform will be available at `http://127.0.0.1:5000`.

## 🎮 Usage Guide

1. **Create an Account**: Sign up and set your technical discipline and seniority level.
2. **Dashboard**: View your overall readiness score and recent mock session histories.
3. **Start Simulation**: Enter the Neural Hub to begin a voice-activated behavioral or coding interview.
4. **Analytics**: Review the Efficiency Roadmap to track your progress over time and toggle specific performance datasets.
5. **Export**: Generate PDF reports of your interviews to share with mentors or recruiters.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page if you want to contribute.

## 📝 License

This project is proprietary and confidential. All rights reserved.
