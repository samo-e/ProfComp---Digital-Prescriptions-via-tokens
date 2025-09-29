# Simulation of electronic prescriptions process through the use of tokens
## Professional Computing - CITS3200
<!-- MD_ONLY_START -->
<p align="center">
<img src="https://img.shields.io/badge/python-3.13.7-blue" alt="Python 3.13.7">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Black">
  <img src="https://img.shields.io/badge/flask-000000?logo=flask&logoColor=white" alt="Flask">
</p>
<!-- MD_ONLY_END -->

An electronic prescription is a digital version of a paper prescription. Since the introduction of this process in May 2020, the Australian healthcare system has seen an uptake with over 189 million electronic prescriptions issued, more than 80,000 prescribers adopting electronic prescribing and at least 98% of all PBS-approved pharmacies having dispensed medications from electronic prescriptions. With efforts underway to expand electronic prescribing in hospitals and aged care settings, the next generation of healthcare requires proficient education and training in this area. For further information about How to get an Electronic prescription, please view this link: https://www.digitalhealth.gov.au/initiatives-and-programs/electronic-prescriptions We, the Pharmacy department at School of Health and Clinical Sciences propose a simulation of part of the dispense process which involves the scanning of a QR code (token presented by patient) thereby transposing patient details into a copy of an electronic prescription (patient's prescription which the doctor has written). These details are then entered into a dispensing system by a pharmacist manually. We have examples of what a screenshot would look like on a patient's phone and the resulting information that would display on the computer once the QR code is scanned. We will require the simulation program to be editable by the Pharmacy Department for future educational purposes. 

**Client:** Jamie Ly, Diana Benino, Anna Tien

**IP:** Open to further discussion about best IP options. 

| Student       | Student No |
|---------------|-----------:|
| Samuel Lewis  |  23366527  |
| Samay Gupta   |  23860508  |
| Anirudh Kumar |  24100961  |
| Zi Hao Chan   |  24116757  |
| David Pang    |  24128968  |
| Zachary Wang  |  24648002  |

<!-- TEACHER_ONLY_START -->
### HOW TO INSTALL
#### Prerequisites
- Python 3.13.7
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
<!-- TEACHER_ONLY_END -->

### Usage
<!-- TEACHER_ONLY_START -->
- #### I am a *Teacher*:
When you log in as a teacher, you'll be greeted by the Teacher Dashboard:
![Screenshot of app](static/images/screenshot-teacher-dashboard.png)
Here, you will find a list of scenarios, and you can find data TODO FILL THIS
From the teacher dashboard


<!-- TEACHER_ONLY_END -->
- #### I am a *Student*:



### Licence
