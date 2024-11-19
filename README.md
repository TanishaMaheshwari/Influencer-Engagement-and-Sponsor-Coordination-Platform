# **Collabify**  
**A platform connecting sponsors with influencers to simplify and streamline collaboration processes.**  

## **Presentation Video**

Watch the Collabify demo here:

<iframe width="560" height="315" src="https://drive.google.com/file/d/1jM8fUDdjlRXNeuOwiXeNzcnbjA6_zbbC/view?usp=sharing" frameborder="0" allowfullscreen></iframe>


---

## **Table of Contents**  
- [Introduction](#introduction)  
- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Setup and Installation](#setup-and-installation)  
- [Usage](#usage)  
- [Future Enhancements](#future-enhancements)  
- [Contributing](#contributing)  

---

## **Introduction**  
Collabify bridges the gap between sponsors and influencers by providing a user-friendly platform for creating and managing sponsorship campaigns. The application enables sponsors to list campaigns, review influencer applications, and finalize collaborations effortlessly. Influencers can browse active campaigns, apply, and track their status in real-time.  

---

## **Features**  
- **Sponsor Dashboard**: Create, manage, and track sponsorship campaigns.  
- **Influencer Dashboard**: Apply for campaigns and monitor application status.  
- **Dynamic Search & Filter**: Find campaigns or influencers easily based on specific criteria.  
- **Automated Notifications**: Email notifications for campaign updates and application responses.  
- **Secure Authentication**: User login and registration with role-based access control.  

---

## **Tech Stack**  
### **Backend**  
- **Python**: Core application logic.  
- **Flask**: Backend framework for API and server-side operations.  
- **SQLAlchemy**: ORM for database management.  

### **Frontend**  
- **Jinja**: Dynamic HTML templating for user-friendly pages.  

### **Database**  
- **SQLite/MySQL**: Persistent data storage.  

### **Other Tools**  
- **HTML, CSS**: Frontend structure and styling.  

---

## **Setup and Installation**  
### **Prerequisites**  
- Python 3.x  
- Pip package manager  

### **Installation**  
1. **Clone the repository**:  
   Clone the Collabify repository to your local machine and navigate to the project directory:  
   ```bash  
   git clone https://github.com/yourusername/collabify.git  
   cd collabify  
   ```  

2. **Set up a virtual environment**:  
   Create and activate a virtual environment to manage dependencies:  
   ```bash  
   python -m venv env  
   source env/bin/activate    # For Linux/Mac  
   env\Scripts\activate       # For Windows  
   ```  

3. **Install dependencies**:  
   Install all the necessary libraries using the `requirements.txt` file:  
   ```bash  
   pip install -r requirements.txt  
   ```  

4. **Set up the database**:  
   - Open the `config.py` file and update database connection settings if needed (e.g., for SQLite or MySQL).  
   - Initialize the database schema:  
     ```bash  
     python setup_db.py  
     ```  

5. **Run the application**:  
   Start the Flask application server:  
   ```bash  
   python app.py  
   ```  

6. **Access the application**:  
   Open your web browser and navigate to:  
   ```  
   http://127.0.0.1:5000  
   ```  

  

---

## **Usage**  
1. **Sponsors**:  
   - Register as a sponsor.  
   - Log in and create new campaigns.  
   - Manage ongoing campaigns and review influencer applications.  

2. **Influencers**:  
   - Register as an influencer.  
   - Browse active sponsorship campaigns.  
   - Apply for campaigns and track application status.  

---

## **Future Enhancements**  
- Integrate payment gateways for seamless transactions.  
- Add an advanced analytics dashboard for sponsors to monitor campaign performance.  
- Develop a mobile-friendly UI for better accessibility.  

---

## **Contributing**  
We welcome contributions from the community!  
1. Fork the repository.  
2. Create a new feature branch:  
   ```bash  
   git checkout -b feature-name  
   ```  
3. Commit your changes:  
   ```bash  
   git commit -m "Add new feature"  
   ```  
4. Push the branch to your forked repository:  
   ```bash  
   git push origin feature-name  
   ```  
5. Open a pull request with a detailed description of your changes.  

---

**You can now explore the Collabify platform!**

