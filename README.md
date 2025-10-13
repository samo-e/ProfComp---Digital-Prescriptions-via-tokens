# Simulation of electronic prescriptions process through the use of tokens
<!-- MD_ONLY_START -->
<p align="center">
   <img src="https://img.shields.io/badge/python-3.13.7-blue" alt="Python 3.13.7">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Black">
  <img src="https://img.shields.io/badge/flask-000000?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/code%20style-prettier-ff69b4" alt="Prettier">
</p>
<!-- MD_ONLY_END -->

<main class="container-fluid"><div class="row">

<div class="col-md-3">

<div style="position: sticky; top: 10%; height: max-content;" class="d-none d-md-block">
   <nav id="navbar-example3" class="h-100 flex-column align-items-stretch pe-4 border-end">
      <nav class="nav nav-pills flex-column">
         <a class="nav-link mb-1" href="#background">Background</a>
         <a class="nav-link mb-1" href="#created-by">Created By</a><!-- TEACHER_ONLY_START -->
         <a class="nav-link mb-1" href="#installation">How to Install</a>
         <nav class="nav nav-pills flex-column">
            <a class="nav-link ms-3 mb-1" href="#prerequisites">Prerequisites</a>
            <a class="nav-link ms-3 mb-1" href="#install">Install</a>
         </nav><!-- TEACHER_ONLY_END -->
         <a class="nav-link mb-1" href="#usage">Usage</a>
         <nav class="nav nav-pills flex-column"><!-- TEACHER_ONLY_START -->
            <a class="nav-link ms-3 mb-1" href="#usage-admin">For Administrators</a>
            <nav class="nav nav-pills flex-column">
               <a class="nav-link ms-5 mb-1" href="#profiles">Profiles</a>
               <a class="nav-link ms-5 mb-1" href="#create-account">Create Account</a>
               <a class="nav-link ms-5 mb-1" href="#download">Download All</a>
            </nav>
            <a class="nav-link ms-3 mb-1" href="#usage-teacher">For Teachers</a>
            <nav class="nav nav-pills flex-column">
               <a class="nav-link ms-5 mb-1" href="#create-scenario">Create Scenarios</a>
               <a class="nav-link ms-5 mb-1" href="#edit-scenario">Edit or Delete Scenarios</a>
               <a class="nav-link ms-5 mb-1" href="#add-pt">Create and Edit Patients</a>
               <a class="nav-link ms-5 mb-1" href="#assign-students">Assigning Students</a>
               <a class="nav-link ms-5 mb-1" href="#submissions">Viewing Submissions</a>
               <a class="nav-link ms-5 mb-1" href="#manage-students">Managing Students</a>
            </nav><!-- TEACHER_ONLY_END -->
            <a class="nav-link ms-3 mb-1" href="#usage-student">For Students</a>
            <nav class="nav nav-pills flex-column">
               <a class="nav-link ms-5 mb-1" href="#making-a-submission">Making a Submission</a>
            </nav>
         </nav>
         <a class="nav-link mb-1" href="#licence">Licence</a>
   </nav>
</div>

</div>

<section class="col-md-9">
<div data-bs-spy="scroll" data-bs-target="#navbar-example3" data-bs-smooth-scroll="true" class="scrollspy-example-2" tabindex="0">


<div id="background">

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
| Flask-Minify     |     0.50 |

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
3. Set up environment variables  
    Linux / Mac
    ```sh
    export SECRET_KEY='your_secret_key_here'
    ```
    Windows (PowerShell)
    ```sh
    setx SECRET_KEY "your_secret_key_here"
    ```
4. Run the "create_admin" script to create a starter admin account
   ```sh
   python flaskr/admin_create.py
   ```
   you will be prompted to enter the following 

   1. Email 
   2. First name 
   3. Last name 
   4. Password
   
5. Run the application
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
<div id="usage-admin">

#### I am an *Administrator*:
<div id="profiles">

##### Profiles Tab

When you log in as a teacher, you'll be greeted by the Admin Dashboard:
![Screenshot of Admin Dashboard](static/images/screenshots/admin/ss-42-profiles.png)

Here you can delete accounts, or click to edit them.

</div><div id="create-account">

##### Account Creation Tab

You can also navigate to the Create Accounts tab where you can make new tabs.  
![Screenshot of Admin Dashboard](static/images/screenshots/admin/ss-40-create-account.png)

Click the green button to add individual accounts or upload a `.csv` files to bulk import files.
When uploading a file, make sure you include the following columns:
| studentnumber | first_name | last_name | email |
|:--------------|:-----------|:----------|:------|

An example is shown below:  
| studentnumber | first_name | last_name | email |
|:--------------|:-----------|:----------|:------|
| 20250123      | Emily      | Stone     | student20@test.com |
| 20250147      | Lucas      | Nguyen    | student21@test.com |
| 20250189      | Sophia     | Martins   | student22@test.com |

You can also add a password field if you would like to use some other program to generate these (see below for example). Please note, we cannot guaruntee the passwords generated are cryptographically secure.  
| studentnumber | first_name | last_name | email | password |
|:--------------|:-----------|:----------|:------|:---------|
| 20250123      | Emily      | Stone     | student20@test.com | password123 |

If you would like to bulk create Teachers or Admins, you can add the role column:
| studentnumber | first_name | last_name | email | role |
|:--------------|:-----------|:----------|:------|:---------|
|       | Valery      | Hawk     | admin100@test.com | admin |
|       | John      | Duley     | teacher1@test.com | admin |

Alternatively, you can manually enter users with the green button.


Once you have confirmed everything is as it should be, press the "Confirm Account Creation" button. This will prompt you to download the file which contains all the generated passwords.  

</div><div id="download">

##### Download All Tab

On the Download All tab, you can download all the student data from the server.  
This will include all students's information, names, emails etc. and also all their submissions along with the respective patient's prescriptions.

</div>

<div id="usage-teacher">

#### I am a *Teacher*:
When you log in as a teacher, you'll be greeted by the Teacher Dashboard:

![Screenshot of Teacher Dashboard](static/images/screenshots/teacher/ss-01-teacher-dashboard.png)

Here, you will find a list of scenarios and some data regarding your cohort.  
From the teacher dashboard, you can
<div id="create-scenario">

##### Creating a New Scenario

To create a new scenario, click the button labelled "Create New Scenario".  
This will add a new scenario to your list of scenarios.  

![Screenshot of Teacher Dashboard after creating a new scenario](static/images/screenshots/teacher/ss-02-teacher-dashboard-scenario-1.png)

Now you can edit, add details and assign students to the scenario.  

</div><div id="view-scenario">

##### Viewing a Scenario

To view a new scenario in more details click a scenario's name in your dashboard or the blue view button to the right.  

</div><div id="edit-scenario">

##### Edit or Delete Scenarios

To delete a scenario, click the red trash icon. This will open a pop-up asking you to confirm. *Please note that after deleting a scenario, it cannot be recovered.  
You can make or edit changes by clicking a scenario's name or the blue edit button to the right.  

![Screenshot of Editing a Scenario](static/images/screenshots/teacher/ss-03-scenario-1.png)

</div><div id="add-pt">

##### Create and Edit Patients

From your dashboard, you can click the yellow "Manage Patients" button to take you to the manage patients menu:  

![Screenshot of Patient Management Dashboard](static/images/screenshots/teacher/ss-10-patient-management.png)

From here, you can edit individual patients, or add new ones.
Clicking on a patient will take you to a page where you can update their details.  
On the edit patient page, you can either fill in the information manually or generate it using the Generate Details button in the top right. After using this button, you can still edit the patient's details.

![Screenshot of Creating a Patient](static/images/screenshots/teacher/ss-11-adding-new-patient.png)

Back on the patient management dashboard, you can click the green eye icon to view a patient's ASL (this is what the student will see).

![Screenshot of Draga Diaz's Active Script List](static/images/screenshots/teacher/ss-13-viewing-a-patients-asl.png)

Back on the patient management dashboard, you can click the blue clip board icon to update a patient's active script list and available local repeats.

![Screenshot of Editing an ASL](static/images/screenshots/teacher/ss-12-editing-a-patients-asl.png)

</div><div id="assign-students">

##### Assign students to scenarios
 
By clicking on the green "Assign Students" for a scenario, you will be navigated to a page where you can assign students to the scenario:  

![Screenshot of Managing Students](static/images/screenshots/teacher/ss-04-assign-students.png)

Here you can decide what tasks students should be allocated to and which patient each student should be allocated to. When you have done so, it will take you back to the scenario dashboard, where you can view the changes you have made.

![Screenshot of Assigned Students](static/images/screenshots/teacher/ss-05-scenario-1-students-assigned.png)

</div><div id="submissions">

##### Viewing Submissions
 
At the bottom of a scenario's dashboard, you can find the button for viewing students' submissions:  

![Screenshot of all submissions](static/images/screenshots/teacher/ss-14-submissions.png)

Clicking on an individual's submission will allow you to submit a grade.  

![Screenshot of a specific students submission](static/images/screenshots/teacher/ss-15-grade-submission.png)

You can see the final ASL the student submitted, any comments, and any documents the student has uploaded.

</div><div id="manage-students">

##### Manage students
 
Click on the green "Manage Students" button in your dashboard to view the student management dashboard:  

![Screenshot of Student Management](static/images/screenshots/teacher/ss-06-student-management.png)

Here you can add new students:  

![Screenshot of Adding a Student](static/images/screenshots/teacher/ss-07-add-student.png)

You can also edit their details or reset their password using the associated buttons next to each student in the table.

</div>
</div>
<hr>
<!-- TEACHER_ONLY_END -->
<div id="usage-student">

#### I am a *Student*:
When you log in as a student, you'll be greeted by the Student Dashboard:

![Screenshot of Student Dashboard](static/images/screenshots/student/ss-20-student-dashboard.png)

From here, you can see the scenarios that have been assigned to you.  
In this example, we will attempt _Scenario 1_:  
After clicking on <i class="bi bi-eye me-1"></i>View Details, you will be redirected to 

![Screenshot of Scenario 1](static/images/screenshots/student/ss-21-scenario-student-view.png)

On this page, you will be able to see what instructions your teacher has set, any required questions for you to answer, and details about the patient.  
You can view this patient's Active Script List (ASL) by clicking on the <i class="bi bi-file-medical me-1"></i>View ASL button: 

![Screenshot of Draga Diaz's Active Script List](static/images/screenshots/teacher/ss-13-viewing-a-patients-asl.png)

Here you can dispense items from the patient's ASL.

<div id="making-a-submission">

##### Making a Submission

Back in viewing a scenario, you can click Submit Work  

![Screenshot of Submitting work for a scenario](static/images/screenshots/student/ss-22-submit-work.png)

Here, you can:
 - Go back and review the patient's ASL
 - Review scenario instructions and your assigned tasks.
 - Submit your completed work, including explanations of your approach and any challenges.
 - Upload supporting documents (PDF, Word, or text; max 10MB each).
 - See the current status of your submission: Not submitted, pending grade, or graded

</div>


</div>
</div>
<hr>

<div id="licence">

### Licence

_Nil licence at this time._

</div>
</div>
</section></div></main>