from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    BooleanField,
    DateField,
    TelField,
    EmailField,
    IntegerField,
    DecimalField,
    TextAreaField,
    FieldList,
    FormField,
    SubmitField,
)
from wtforms.validators import (
    length,
    Email,
    NumberRange,
    DataRequired,
    Regexp,
    Optional,
    ValidationError,
)
from datetime import datetime

DEFAULT_CHOICE = ("", "")


class BasicDetailsSubForm(FlaskForm):
    # Personal
    lastName = StringField("Surname")
    givenName = StringField("Given name")
    title = SelectField(
        "Title",
        choices=[
            DEFAULT_CHOICE,
            ("ms", "Ms"),
            ("mrs", "Mrs"),
            ("mr", "Mr"),
            ("rev", "Rev"),
            ("dr", "Dr"),
            ("honorable", "Honorable"),
        ],
    )
    sex = SelectField(
        "Sex", choices=[DEFAULT_CHOICE, ("male", "Male"), ("female", "Female")]
    )
    dob = DateField("Date of Birth", format="%Y-%m-%d", validators=[Optional()])
    ptNumber = StringField("Patient No.")

    # Contact
    suburb = StringField("Suburb")
    state = SelectField(
        "State",
        choices=[
            DEFAULT_CHOICE,
            ("act", "ACT"),
            ("nt", "NT"),
            ("nsw", "NSW"),
            ("qld", "QLD"),
            ("sa", "SA"),
            ("tas", "TAS"),
            ("vic", "VIC"),
            ("wa", "WA"),
        ],
    )
    postcode = IntegerField("Postcode")
    phone = TelField("Phone No.")
    mobile = TelField("Mobile No.")
    licence = StringField("Licence No.")
    smsRepeats = BooleanField("SMS Repeat Reminders", default=False)
    smsOwing = BooleanField("SMS Owing Reminders", default=False)
    email = EmailField("Email", validators=[Email()])

    # Medicare
    medicare = StringField(
        "Medicare No.",
        validators=[
            DataRequired(),
            length(min=9, max=9, message="Medicare number must be 9 digits"),
            Regexp("^[0-9]*$", message="Medicare number must contain only digits"),
        ],
    )
    medicareIssue = IntegerField(validators=[NumberRange(min=0, max=9)])
    medicareValidTo = StringField("Valid To")  # can also use custom validator
    medicareSurname = StringField("Surname")
    medicareGivenName = StringField("Given name")

    # Concession
    concessionNumber = StringField("Concession No.")
    concessionValidTo = DateField(
        "Valid To", format="%Y-%m-%d", validators=[Optional()]
    )
    safetyNetNumber = StringField("Safety Net No.")
    repatriationNumber = StringField("Repatriation No.")
    repatriationValidTo = DateField(
        "Valid To", format="%Y-%m-%d", validators=[Optional()]
    )
    repatriationType = StringField("Repatriation Type")
    ndssNumber = StringField("NDSS No.")

    # MyHR
    ihiNumber = StringField("IHI No.")
    ihiStatus = StringField("IHI Status")
    ihiRecordStatus = StringField("Record Status")

    # Doctor
    doctor = StringField("Default Doctor")

    # Other Checkboxes
    ctgRegistered = BooleanField("CTG Registered", default=False)
    genericsOnly = BooleanField("Generics Only", default=False)
    repeatsHeld = BooleanField("Repeats Held", default=False)
    ptDeceased = BooleanField("Patient Deceased", default=False)


class SafetyNetDetailsSubForm(FlaskForm):
    # Individual
    script_count_outside = DecimalField(validators=[NumberRange(min=0), Optional()])
    script_count_inside = IntegerField(  # FIELD SHOULD BE IGNORED WHEN INPUT
        render_kw={"disabled": True}
    )
    script_count_total = IntegerField(  # FIELD SHOULD BE IGNORED WHEN INPUT
        render_kw={"disabled": True}
    )
    scripts_value_outside = DecimalField(
        places=2,  # ensures step="0.01" for dollar amounts
        validators=[NumberRange(min=0.00), Optional()],
        render_kw={"step": "0.01", "min": "0.00"},
    )
    scripts_value_inside = DecimalField(  # FIELD SHOULD BE IGNORED WHEN INPUT
        places=2,
        default=0.00,
        validators=[NumberRange(min=0.00), Optional()],
        render_kw={"step": "0.01", "min": "0.00", "disabled": True},
    )
    scripts_value_total = DecimalField(  # FIELD SHOULD BE IGNORED WHEN INPUT
        places=2,
        default=0.00,
        validators=[NumberRange(min=0.00), Optional()],
        render_kw={"step": "0.01", "min": "0.00", "disabled": True},
    )

    # Family
    family_name = StringField("Family Name")
    family_script_count_outside = DecimalField(  # FIELD SHOULD BE IGNORED WHEN INPUT
        validators=[NumberRange(min=0), Optional()]
    )
    family_script_count_inside = IntegerField(  # FIELD SHOULD BE IGNORED WHEN INPUT
        render_kw={"disabled": True}
    )
    family_script_count_total = IntegerField(  # FIELD SHOULD BE IGNORED WHEN INPUT
        render_kw={"disabled": True}
    )
    family_scripts_value_outside = DecimalField(  # FIELD SHOULD BE IGNORED WHEN INPUT
        places=2,  # ensures step="0.01" for dollar amounts
        validators=[NumberRange(min=0.00), Optional()],
        render_kw={"step": "0.01", "min": "0.00"},
    )
    family_scripts_value_inside = DecimalField(  # FIELD SHOULD BE IGNORED WHEN INPUT
        places=2,
        default=0.00,
        validators=[NumberRange(min=0.00), Optional()],
        render_kw={"step": "0.01", "min": "0.00", "disabled": True},
    )
    family_scripts_value_total = DecimalField(  # FIELD SHOULD BE IGNORED WHEN INPUT
        places=2,
        default=0.00,
        validators=[NumberRange(min=0.00), Optional()],
        render_kw={"step": "0.01", "min": "0.00", "disabled": True},
    )

    class FamilyMember(FlaskForm):
        name = StringField("Name")
        type = StringField("Type")

    family_members = FieldList(FormField(FamilyMember))


class AllergiesSubForm(FlaskForm):
    pass


class AccountsSubForm(FlaskForm):
    # Facility Details
    facility = StringField("Facility:")
    ward = StringField("Ward")
    room = StringField("Room No")
    bed = StringField("Bed No")
    ptCat = SelectField("Patient Category", choices=[DEFAULT_CHOICE])
    chartStart = DateField("Chart Start", format="%Y-%m-%d", validators=[Optional()])
    chartEnd = DateField("Chart End", format="%Y-%m-%d", validators=[Optional()])
    chartDuration = SelectField("Chart Duration", choices=[DEFAULT_CHOICE])

    # Debtor Account Details
    class DebtorAccsRowForm(FlaskForm):
        account = StringField("Account#")
        description = StringField("Description")
        group = StringField("Group")
        current = StringField("Current")
        days30 = StringField("30 Days")
        days60 = StringField("60 Days")
        days90 = StringField("90 Days")
        total_bal = StringField("Total Bal")
        status = StringField("Status")

    debtorAccs = FieldList(FormField(DebtorAccsRowForm), min_entries=0)

    # Stock Transfers
    canTfrStockToCustomer = BooleanField(
        "Can transfer stock to this customer", default=False
    )

    # Auto Charging Details
    autoChargeScripts = BooleanField(
        "Auto charge scripts for this patient", default=False
    )
    linkToDebtorAcc = BooleanField("Link to debtor account", default=False)
    linkedClientAcc = StringField("Linked client account:")
    debtorAcc = SelectField("Debtor account:", choices=[DEFAULT_CHOICE])
    notSendScriptsToTill = BooleanField(
        "Do not send scripts to Till for this patient", default=False
    )
    notDeductStocks = BooleanField(
        "Do not deduct stocks for this patient", default=False
    )


class NotesSubForm(FlaskForm):
    content = TextAreaField("Patient Notes")
    last_edited = StringField("Last Edited", render_kw={"readonly": True})


class ClinicalInterventionsSubForm(FlaskForm):
    pass


class SMSSubForm(FlaskForm):
    pass


class ClubsSubForm(FlaskForm):
    class ClubRowForm(FlaskForm):
        name = StringField("Name")
        card_no = StringField("CardNo")
        membership_expiry = StringField("Membership Expiry")

    class ProvidersRowForm(FlaskForm):
        name = StringField("Name")
        member_no = StringField("CardNo")
        identifier = StringField("Identifier")
        membership_expiry = StringField("Membership Expiry")

    clubs = FieldList(FormField(ClubRowForm), min_entries=0)
    providers = FieldList(FormField(ClubRowForm), min_entries=0)


class OtherSubForm(FlaskForm):
    pbsDiscount = StringField("PBS Discount (Default)")
    defaultRepeatPrint = SelectField("Default Repeat Print", choices=[DEFAULT_CHOICE])
    ignoreMinMedCount = BooleanField("Ignore Minimum Medication Count For DAA Export")
    # eScripts
    eScriptsRepeatMethod = SelectField(
        "Repeat Token Method",
        choices=[
            ("default", "Default (eScript Details)"),
            ("sms", "SMS"),
            ("email", "Email"),
            ("none", "Don't Send"),
        ],
    )


class PatientForm(FlaskForm):
    basic = FormField(BasicDetailsSubForm)
    safetyNet = FormField(SafetyNetDetailsSubForm)
    allergies = FormField(AllergiesSubForm)
    accounts = FormField(AccountsSubForm)
    notes = FieldList(FormField(NotesSubForm))
    clinical = FormField(ClinicalInterventionsSubForm)
    sms = FormField(SMSSubForm)
    clubs = FormField(ClubsSubForm)
    other = FormField(OtherSubForm)


# forms.py
class ASLForm(FlaskForm):
    # Contacts (Carer/Agent)
    carer_name = StringField("Carer Name", validators=[Optional()])
    carer_relationship = StringField("Carer Relationship", validators=[Optional()])
    carer_mobile = StringField("Carer Mobile", validators=[Optional()])
    carer_email = StringField("Carer Email", validators=[Optional()])

    # Preferred Contact
    preferred_contact = SelectField(
        "Preferred Contact",
        choices=[
            ("mobile", "Mobile"),
            ("home", "Home"),
            ("email", "Email"),
        ],
        validators=[Optional()],
    )

    # Consent
    consent_status = SelectField(
        "Consent",
        choices=[
            ("0", "No Consent"),
            ("1", "Pending"),
            ("2", "Granted"),
            ("3", "Rejected"),
        ],
        default="1",
    )

    # Notes
    notes = TextAreaField("Notes", validators=[Optional()])


class DeleteForm(FlaskForm):
    submit = SubmitField("Delete")


class EmptyForm(FlaskForm):
    pass


class ASL_ConsentStatusForm(FlaskForm):
    is_registered = SelectField(
        "Is Registered",
        choices=[
            ("true", "Yes"),
            ("false", "No"),
        ],
        validators=[DataRequired()],
    )
    status = SelectField(  # required
        "Status",
        choices=[
            ("", "Select..."),
            ("NO CONSENT", "No Consent"),
            ("PENDING", "Pending"),
            ("GRANTED", "Granted"),
            ("REJECTED", "Rejected"),
        ],
        validators=[DataRequired()],
    )
    last_updated = StringField(
        "Last Updated",
        validators=[DataRequired()],
        render_kw={"placeholder": "DD/MM/YYYY HH:MM am/pm"},
        default=lambda: datetime.now().strftime("%d/%m/%Y %H:%M %p"),
    )


class ASL_ALR_PrescriberSubform(FlaskForm):
    fname = StringField("First Name", validators=[Optional()])
    lname = StringField("Last Name", validators=[Optional()])
    title = StringField("Title / Qualifications", validators=[Optional()])
    address_1 = StringField("Address", validators=[Optional()])
    prescriber_id = IntegerField(
        "Prescriber ID", validators=[Optional(), NumberRange(min=1)]
    )
    phone = StringField("Phone", validators=[Optional(), length(max=20)])
    fax = StringField("Fax", validators=[Optional(), length(max=20)])


class ASL_ALR_PrescriptionSubform(FlaskForm):
    prescription_id = IntegerField(
        "Prescription ID", validators=[Optional(), NumberRange(min=1)]
    )
    paperless = SelectField(
        "Paperless",
        choices=[("true", "True"), ("false", "False")],
        validators=[Optional()],
    )
    prescribed_date = StringField(
        "Prescribed Date",
        validators=[Optional(), Regexp(r"^\d{2}/\d{2}/\d{4}$", message="DD/MM/YYYY")],
        render_kw={"placeholder": "DD/MM/YYYY"},
    )
    dispensed_date = StringField(
        "Last Dispensed Date",
        validators=[Optional(), Regexp(r"^\d{2}/\d{2}/\d{4}$", message="DD/MM/YYYY")],
        render_kw={"placeholder": "DD/MM/YYYY"},
    )
    drug_name = TextAreaField("Drug Name", validators=[Optional()])
    dose_instr = StringField(
        "Dose Instructions",
        validators=[Optional()],
        render_kw={"placeholder": 'e.g. "ONCE PER DAY" or "AS REQUIRED"'},
    )
    dose_qty = IntegerField("Dose Qty", validators=[Optional(), NumberRange(min=1)])
    dose_rpt = IntegerField(
        "Dose Repeats (Remaining)", validators=[Optional(), NumberRange(min=0)]
    )
    brand_sub_not_prmt = SelectField(
        "Brand Substitution Not Permitted",
        choices=[("true", "True"), ("false", "False")],
        validators=[Optional()],
    )

    prescriber = FormField(ASL_ALR_PrescriberSubform)


class ASL_ALR_CreationForm(FlaskForm):
    consent_status = FormField(ASL_ConsentStatusForm)
    asl_creations = FieldList(FormField(ASL_ALR_PrescriptionSubform))
    alr_creations = FieldList(FormField(ASL_ALR_PrescriptionSubform))
