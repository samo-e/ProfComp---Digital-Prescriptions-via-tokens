# Simulation of electronic prescriptions process through the use of tokens
<!-- MD_ONLY_START -->
<p align="center">
<img src="https://img.shields.io/badge/python-3.13.7-blue" alt="Python 3.13.7">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Black">
  <img src="https://img.shields.io/badge/flask-000000?logo=flask&logoColor=white" alt="Flask">
</p>
<!-- MD_ONLY_END -->

<main class="container-fluid"><div class="row">

<div class="col-md-3">

<div style="position: sticky; top: 10%; height: max-content;" class="d-none d-md-block">
   <nav id="navbar-example3" class="h-100 flex-column align-items-stretch pe-4 border-end">
      <nav class="nav nav-pills flex-column">
         <a class="nav-link" href="#background">Background</a>  
         <a class="nav-link" href="#created-by">Created By</a>  
         <a class="nav-link" href="#installation">How to Install</a>  
         <nav class="nav nav-pills flex-column">
            <a class="nav-link ms-3 my-1" href="#prerequisites">Prerequisites</a>  
            <a class="nav-link ms-3 my-1" href="#install">Install</a>  
         </nav>
         <a class="nav-link" href="#usage">Usage</a>  
         <nav class="nav nav-pills flex-column">
            <a class="nav-link ms-3 my-1" href="#usage-teacher">For Teachers</a>  
            <a class="nav-link ms-3 my-1" href="#usage-student">For Students</a>  
         </nav>
         <a class="nav-link" href="#licence">Licence</a>  
   </nav>
</div>

</div>

<section class="col-md-9">
<div data-bs-spy="scroll" data-bs-target="#navbar-example3" data-bs-smooth-scroll="true" class="scrollspy-example-2" tabindex="0">


<div id="background">

### Background
An electronic prescription is a digital version of a paper prescription. Since the introduction of this process in May 2020, the Australian healthcare system has seen an uptake with over 189 million electronic prescriptions issued, more than 80,000 prescribers adopting electronic prescribing and at least 98% of all PBS-approved pharmacies having dispensed medications from electronic prescriptions. With efforts underway to expand electronic prescribing in hospitals and aged care settings, the next generation of healthcare requires proficient education and training in this area.  
For further information about how to get an Electronic prescription, please view [this link](https://www.digitalhealth.gov.au/initiatives-and-programs/electronic-prescriptions).  
We, the Pharmacy department at School of Health and Clinical Sciences propose a simulation of part of the dispense process which involves the scanning of a QR code (token presented by patient) thereby transposing patient details into a copy of an electronic prescription (patient's prescription which the doctor has written). These details are then entered into a dispensing system by a pharmacist manually. We have examples of what a screenshot would look like on a patient's phone and the resulting information that would display on the computer once the QR code is scanned.  
We will require the simulation program to be editable by the Pharmacy Department for future educational purposes.

**Client:** Jamie Ly, Diana Benino, Anna Tien

**IP:** Open to further discussion about best IP options. 

</div>

<hr>

<div id="created-by">

##### This web app was created by the following students as part of the Professional Computing (CITS3200) assignment.
| Student       | Student No |
|---------------|-----------:|
| Samuel Lewis  |  23366527  |
| Samay Gupta   |  23860508  |
| Anirudh Kumar |  24100961  |
| Zi Hao Chan   |  24116757  |
| David Pang    |  24128968  |
| Zachary Wang  |  24648002  |

<hr>

</div>

<!-- TEACHER_ONLY_START -->

<div id="installation">

### How to Install

<div id="prerequisites">

#### Prerequisites
- Python 3.13.7
- Python modules found in requirements.txt:

| Module           | Vers. No |
|------------------|---------:|
| Flask            |    2.3.3 |
| Flask-SQLAlchemy |    3.0.5 |
| Flask-Login      |    0.6.2 |
| Flask-WTF        |    1.1.1 |
| Werkzeug         |    2.3.7 |
| WTForms          |    3.0.1 |
| SQLAlchemy       |   2.0.20 |
| markdown-it-py   |    4.0.0 |

</div>
<div id="install">

#### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```
2. Install dependencies
   ```sh
   pip install -r requirements.txt
   ```
3. Setup environment variables  
    Linux / Mac
    ```sh
    export SECRET_KEY='your_secret_key_here'
    ```
    Windows (Powershell)
    ```sh
    setx SECRET_KEY "your_secret_key_here"
    ```
4. Run the application
   ```sh
   flask run
   ```

</div>
</div>
<hr>

<!-- TEACHER_ONLY_END -->
<div id="usage">

### Usage
<!-- TEACHER_ONLY_START -->
<div id="usage-teacher">

#### I am a *Teacher*:
When you log in as a teacher, you'll be greeted by the Teacher Dashboard:

![Screenshot of Teacher Dashboard](static/images/screenshot-teacher-dashboard.png)

Here, you will find a list of scenarios and some data regarding your cohort.  
From the teacher dashboard, you can
 - Create a new scenario  
To create a new scenario, click the blue button labelled "New Scenario".  
This will add a new scenario to your list of scenarios.  
 - Edit or Delete scenarios  
You can make or edit changes by clicking a scenario's name or the blue edit button to the right.  
To delete a scenario, click the red trash icon. This will open a popup asking you to confirm. *Please note, after deleting a scenario, it cannot be recovered.  

![Screenshot of Editing a Scenario](static/images/screenshot-scenario.png)

 - Create and Edit patients  // TODO - run through creation of patient  
 - Assign students to scenarios  // TODO - run through this  
 - Manage students  // TODO - show how to manage students  
</div>
<hr>
<!-- TEACHER_ONLY_END -->
<div id="usage-student">

#### I am a *Student*:
When you log in as a student, you'll be greeted by the Student Dashboard:

![Screenshot of Student Dashboard](static/images/screenshot-student-dashboard.png)

From here, you can see the scenarios that have been assigned to you, or you can work on one of the practice patients.  
We will attempt _Practice Patient 1: Draga Diaz_:  
After clicking on Draga Diaz, you will be redirected to her Active Script List (ASL):

![Screenshot of Draga Diaz's Active Script List](static/images/screenshot-asl-draga-diaz.png)

Here, you can
 - View Draga's details
 - Print her ASL
 - Request, Delete or Refresh her consent for you to access her ASL  
Requesting or refreshing follows a cycle from <i>No Consent</i> → <i style="color: orange;">Pending</i> → <i style="color: green;">Granted</i>. Click [here](https://help.zsoftware.com.au/hc/en-us/articles/4408453843853-Active-Script-List-ASL) for more info regarding how ASL consent works.
 - Comment on changes that have been made

</div>
</div>
<hr>

<div id="licence">

### Licence

</div>
</div>
</section></div></main>