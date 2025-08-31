from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, DateField, TelField, EmailField, IntegerField
from wtforms.validators import length, Optional, Email

DEFAULT_CHOICE = ("", "")
class PatientForm(FlaskForm):
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
