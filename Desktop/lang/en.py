# coding: utf-8

# Strings in English

class StringsEN:
    def __init__(self):
        self.code = "en"
        self.name = "English"
        self.TITLE = "Register of certificates"
        self.PARAMETERS_BUTTON = "Settings"
        self.PRINT_BUTTON = "Print"
        self.MEMBER_CB = "Member"
        self.CATEG_CB = "Category"
        self.CERT_CB = "Certificate"
        self.AWARD_CERTIFICATE = "Award certificate"
        self.REVOKE_CERTIFICATE = "Revoke certificate"
        self.MAKE_CERTIFICATOR_BUTTON = "Make Certificator"
        self.REINITIALIZE_BUTTON = "Reinitialize"
        self.SAVED = "Saved"
        self.SAVING = "Saving..."
        self.SYNCHRONIZING = "Synchronizing..."
        self.INVALID_REGISTER_VALUE = "Invalid value in register"
        self.DELETE_CATEGORY_Q = "Delete category ?"
        self.ADVANCED = "Advanced"
        self.HIDE = "Hide"
        self.CREATE_LOAD_REGISTER = "Create/Load register"
        self.DELETE_REGISTER = "Delete register"
        self.MEMBER_LIST = "List of members :"
        self.ADD_MEMBER = "Add member :"
        self.FIRST_NAME = "First name"
        self.LAST_NAME = "Last Name"
        self.VALIDATE = "Validate"
        self.REMOVE_MEMBER = "Remove member"
        self.CATEGORIES = "Categories :"
        self.CERTIFICATES = "Certificates :"
        self.ADD_CERTIFICATE = "Add certificate :"
        self.CATEGORY = "Category"
        self.CERTIFICATE_NAME = "Certificate name"
        self.DELETE_CERTIFICATE = "Delete Certificate"
        self.DELETE_CATEGORY = "Delete Category"
        self.CLICK_HERE_TO_BEGIN = "Click here to begin : "
        self.ERROR = "Error"
        self.LOAD_OR_CREATE_REGISTER = "Load or create a register"
        self.SCHOOL = "School :"
        self.ENTER_NAME = "Enter name"
        self.PASSWORD = "Password :"
        self.CONFIRM_PASSWORD = "Confirm password :"
        self.PASSWORDS_DONT_MATCH = "The passwords do not match"
        self.CREATE_REGISTER = "Create register"
        self.LOAD_REGISTER = "Load register"
        self.ERROR_DURING_SCHOOL_LIST_DOWNLOAD = "An error occurred when downloading the list of school names"
        self.ERROR_WHEN_CREATING_REGISTER = "An error occurred when creating the register"
        self.AUTHORIZATION_REQUIRED = "Authorization required"
        self.ENTER_PASSWORD = "Enter password"
        self.WRONG_PASSWORD = "Wrong password"
        self.AUTHENTICATION_ERROR = "Athentication error"
        self.ERROR_DURING_REGISTER_DELETION = "An error occurred when trying to delete the register. Please try again."
        self.ERROR_WHILE_LOADING_REGISTER = "An error occurred when trying to load the register. Please try again."
        self.ERROR_WHILE_UPLOADING_REGISTER = "An error occurred when trying to upload the register. Please try again."
        self.REGISTER = "Register"
        self.REGISTER_OF_CERTIFICATES = "Register of certificates"
        self.CANT_OPEN_LIBREOFFICE = "Couldn't open LibreOffice. Please open the file manually."
        self.CHECK_INTERNET_CONNECTION = "Please check your internet connection."
        self.CONFIRM = "Confirm"
        self.CONFIRMATION = "Confirmation"
        self.INFORMATION = "Information"
        self.SELECT_LANGUAGE = "Select language"
        self.LANGUAGE = "Language : "

    def REMOVE_CERTIFICATE_FROM(self, m, c):
        return f"Revoke {m}'s {c} certificate ?"

    def AWARD_CERTIFICATE_TO(self, m, c):
        return f"Award the {c} certificate to {m} ?"

    def MAKE_CERTIFICATOR(self, m, c):
        return f"Make {m} a certificator for the {c} certificate ?"

    def CLEAR_HISTORY(self, m, c):
        return f"Erase {m}'s history with the {c} certificate ?"

    def MEMBER_ALREADY_EXISTS(self, firstname, surname):
        return f"A member named {firstname} {surname} already exists."

    def CERTIFICATE_ALREADY_EXISTS(self, c, cat):
        return f"The {c} certificate already exists in category \"{cat}\""

    def DOESNT_HAVE_CERTIFICATE(self, m, c):
        return f"{m} does not have the {c} certificate"

    def DOESNT_HAVE_CERTIFICATE_ANYMORE(self, m, c):
        return f"{m} no longer has the {c} certificate"

    def IS_CERTIFICATOR(self, m, c):
        return f"{m} is a certificator for the {c} certificate."

    def HAS_CERTIFICATE(self, m, c):
        return f"{m} has the {c} certificate."

    def HAS_CERTIFICATES(self, m, l):
        msg = ""
        if len(l) == 1: msg = f"{m} has the following certificate : {l[0]}"
        elif len(l) >= 2:
            msg = f"{m} has the following certificates : "
            for i in range(len(l)):
                if i < len(l) - 1:
                    msg += f"{l[i]}, "
                else:
                    msg += f"and {l[i]}."

        return msg

    def CERTIFICATORS_ARE(self, c, certificators):
        msg = f"The following people are certificators for the {c} certificate : "
        if len(certificators) == 1: msg += certificators[0]
        else:
            for i in range(len(certificators)):
                if i < len(certificators) - 1:
                    msg += f"{certificators[i]}, "
                else:
                    msg += f"and {certificators[i]}."
        if not certificators:
            msg = f"There are no certificators for the {c} certificate at the moment."

        return msg

    def X_CAT_CERTIFICATES(self, category):
        return f"{category} certificates :"

    def CREATE_REGISTER_FOR_SCHOOL(self, school):
        return f"Create a register for school {school} ?"

    def REGISTER_FOR_SCHOOL_HAS_BEEN_CREATED(self, school):
        return f"The register for school {school} was successfully created."

    def REGISTER_FOR_SCHOOL_HAS_BEEN_LOADED(self, school):
        return f"The register for school {school} was successfully loaded."

    def DELETE_REGISTER_FOR_SCHOOL(self, school):
        return f"Delete the whole register of certificates for school {school} (all data will be lost) ?"

