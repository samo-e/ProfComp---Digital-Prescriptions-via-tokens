from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, DateField, TelField, EmailField, IntegerField, DecimalField, TextAreaField, FieldList
from wtforms.validators import length, Optional, Email, NumberRange

DEFAULT_CHOICE = ("", "")
class PatientForm(FlaskForm):
    ### BASIC DETAILS
    # Personal
    lastName = StringField("Surname")
    givenName = StringField("Given name")
    title = SelectField("Title", choices=[DEFAULT_CHOICE,
        ("ms", "Ms"), ("mrs", "Mrs"), ("mr", "Mr"),
        ("rev", "Rev"), ("dr", "Dr"), ("honorable", "Honorable")
    ])
    sex = SelectField("Sex", choices=[DEFAULT_CHOICE, ("male", "Male"), ("female", "Female")])
    dob = DateField("Date of Birth", format="%Y-%m-%d")
    ptNumber = StringField("Patient No.")

    # Contact
    suburb = StringField("Suburb")
    state = SelectField("State", choices=[
        DEFAULT_CHOICE,
        ("act", "Australian Capital Territory"),
        ("nt", "Northern Territory"),
        ("nsw", "New South Wales"),
        ("qld", "Queensland"),
        ("sa", "South Australia"),
        ("tas", "Tasmania"),
        ("vic", "Victoria"),
        ("wa", "Western Australia"),
    ])
    postcode = IntegerField("Postcode")
    phone = TelField("Phone No.")
    mobile = TelField("Mobile No.")
    licence = StringField("Licence No.")
    smsRepeats = BooleanField("SMS Repeat Reminders", default=False)
    smsLastRepeats = BooleanField("SMS Last Repeat Reminders", default=False)
    smsOwing = BooleanField("SMS Owing Reminders", default=False)
    email = EmailField("Email", validators=[Email()])

    # Medicare
    medicare = IntegerField("Medicare No.",[length(min=9, max=9)])
    medicareIssue = IntegerField(validators=[length(min=1, max=1)])
    medicareValidTo = StringField("Valid To")  # can also use custom validator
    medicareSurname = StringField("Surname")
    medicareGivenName = StringField("Given name")

    # Concession
    concessionNumber = StringField("Concession No.")
    concessionValidTo = DateField("Valid To", format="%Y-%m-%d")
    safetyNetNumber = StringField("Safety Net No.")
    repatriationNumber = StringField("Repatriation No.")
    repatriationValidTo = DateField("Valid To", format="%Y-%m-%d", validators=[Optional()])
    repatriationType = StringField("Repatriation Type")
    ndssNumber = StringField("NDSS No.")

    # MyHR
    ihiNumber = StringField("IHI No.")
    ihiStatus = StringField("IHI Status")
    ihiRecordStatus = StringField("Record Status")

    # Doctor
    doctor = StringField("Default Doctor")


    ### SAFETY NET DETAILS
    # Individual
    script_count_outside = DecimalField(
        places=2,  # ensures step="0.01" for dollar amounts
        validators=[NumberRange(min=0.01)],
        render_kw={"step": "0.01", "min": "0.01"})
    script_count_inside = IntegerField( # FIELD SHOULD BE IGNORED WHEN INPUT
        render_kw={"disabled": True})
    script_count_total = IntegerField( # FIELD SHOULD BE IGNORED WHEN INPUT
        render_kw={"disabled": True})
    scripts_value_outside = DecimalField(
        places=2,
        validators=[NumberRange(min=0.00)],
        render_kw={"step": "0.01", "min": "0.00"})
    scripts_value_inside = DecimalField( # FIELD SHOULD BE IGNORED WHEN INPUT
        places=2,
        default=0.00,
        validators=[NumberRange(min=0.00)],
        render_kw={"step": "0.01", "min": "0.00", "disabled": True})
    scripts_value_total = DecimalField( # FIELD SHOULD BE IGNORED WHEN INPUT
        places=2,
        default=0.00,
        validators=[NumberRange(min=0.00)],
        render_kw={"step": "0.01", "min": "0.00", "disabled": True})
    # Family
    family_name = StringField("Family Name", render_kw={"disabled": True})
    
    ### ALLERGIES/HEALTH
    ### ACCOUNTS
    ### NOTES
    patient_notes = FieldList(
        TextAreaField("Patient Notes", validators=[Optional()])
    )
    # Need to pass in each of the patient_notes_last_updated
    ### CLINICAL INTERVENTIONS
    ### SMS
    ### CLUBS
