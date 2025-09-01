from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, DateField, TelField, EmailField, IntegerField, DecimalField, TextAreaField, FieldList, FormField
from wtforms.validators import length, Email, NumberRange

DEFAULT_CHOICE = ("", "")
class BasicDetailsSubForm(FlaskForm):
    # Personal
    lastName = StringField("Surname")
    givenName = StringField("Given name")
    title = SelectField("Title", choices=[DEFAULT_CHOICE,
        ("ms", "Ms"), ("mrs", "Mrs"), ("mr", "Mr"),
        ("rev", "Rev"), ("dr", "Dr"), ("honorable", "Honorable")
    ])
    sex = SelectField("Sex", choices=[DEFAULT_CHOICE, ("male", "Male"), ("female", "Female")])
    dob = DateField("Date of Birth", format="%d-%m-%Y")
    ptNumber = StringField("Patient No.")

    # Contact
    suburb = StringField("Suburb")
    state = SelectField("State", choices=[
        DEFAULT_CHOICE,
        ("act", "ACT"),
        ("nt", "NT"),
        ("nsw", "NSW"),
        ("qld", "QLD"),
        ("sa", "SA"),
        ("tas", "TAS"),
        ("vic", "VIC"),
        ("wa", "WA"),
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
    concessionValidTo = DateField("Valid To", format="%d-%m-%Y")
    safetyNetNumber = StringField("Safety Net No.")
    repatriationNumber = StringField("Repatriation No.")
    repatriationValidTo = DateField("Valid To", format="%d-%m-%Y")
    repatriationType = StringField("Repatriation Type")
    ndssNumber = StringField("NDSS No.")

    # MyHR
    ihiNumber = StringField("IHI No.")
    ihiStatus = StringField("IHI Status")
    ihiRecordStatus = StringField("Record Status")

    # Doctor
    doctor = StringField("Default Doctor")

class SafetyNetDetailsSubForm(FlaskForm):
    # Individual
    script_count_outside = DecimalField(
        validators=[NumberRange(min=0)])
    script_count_inside = IntegerField( # FIELD SHOULD BE IGNORED WHEN INPUT
        render_kw={"disabled": True})
    script_count_total = IntegerField( # FIELD SHOULD BE IGNORED WHEN INPUT
        render_kw={"disabled": True})
    scripts_value_outside = DecimalField(
        places=2,  # ensures step="0.01" for dollar amounts
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

class AllergiesSubForm(FlaskForm):
    pass

class AccountsSubForm(FlaskForm):
    pass

class NotesSubForm(FlaskForm):
    content = TextAreaField("Patient Notes")
    last_edited = StringField("Last Edited", render_kw={"readonly": True})

class ClinicalInterventionsSubForm(FlaskForm):
    pass

class SMSSubForm(FlaskForm):
    pass

class ClubsSubForm(FlaskForm):
    pass

class OtherSubForm(FlaskForm):
    pbsDiscount = StringField("PBS Discount (Default)")
    defaultRepeatPrint = SelectField("Default Repeat Print", choices=[DEFAULT_CHOICE])
    ignoreMinMedCount = BooleanField("Ignore Minimum Medication Count For DAA Export")
    # eScripts
    eScriptsRepeatMethod = SelectField("Repeat Token Method", choices=[
        ("default", "Default (eScript Details)"),
        ("sms", "SMS"),
        ("email", "Email"),
        ("none", "Don't Send")
    ])


class PatientForm(FlaskForm):
    basic     = FormField(BasicDetailsSubForm)
    safetyNet = FormField(SafetyNetDetailsSubForm)
    allergies = FormField(AllergiesSubForm)
    accounts  = FormField(AccountsSubForm)
    notes     = FieldList(FormField(NotesSubForm))
    clinical  = FormField(ClinicalInterventionsSubForm)
    sms       = FormField(SMSSubForm)
    clubs     = FormField(ClubsSubForm)
    other     = FormField(OtherSubForm)
