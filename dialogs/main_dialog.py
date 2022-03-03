# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.core import MessageFactory, UserState
from botbuilder.azure import BlobStorage, BlobStorageSettings
from botbuilder.ai.luis import LuisApplication, LuisPredictionOptions, LuisRecognizer

from entity import UserProfile
from dialogs.reg_dialog import RegDialog
from dialogs.help_dialog import HelpDialog
from dialogs.crono_dialog import CronoDialog
from dialogs.find_dialog import FindDialog
from dialogs.info_dialog import InfoDialog
from dotenv import load_dotenv,find_dotenv
import os

load_dotenv(dotenv_path="var.env")
CONTAINER_NAME=os.getenv("BLOB_CONTAINER_NAME")
CONTAINER_STRING=os.getenv("BLOB_CONNECTION_STRING")
LUIS_ID=os.getenv("LUIS_API_ID")
LUIS_KEY=os.getenv("LUIS_API_KEY")
LUIS_ENDPOINT=os.getenv("LUIS_ENDPOINT")


class MainDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self.user_state = user_state
        self.add_dialog(InfoDialog(InfoDialog.__name__))
        self.add_dialog(RegDialog(RegDialog.__name__))
        self.add_dialog(CronoDialog(CronoDialog.__name__))
        self.add_dialog(FindDialog(FindDialog.__name__))
        self.add_dialog(HelpDialog(HelpDialog.__name__))
        self.add_dialog(
            WaterfallDialog("WFDialog", [self.initial_step, self.final_step])
        )

        self.initial_dialog_id = "WFDialog"
        blob_settings = BlobStorageSettings(
            container_name=CONTAINER_NAME,
            connection_string=CONTAINER_STRING
        )
        self.storage = BlobStorage(blob_settings)
        luisapp=LuisApplication(LUIS_ID,LUIS_KEY,LUIS_ENDPOINT)
        luisoption= LuisPredictionOptions(include_all_intents=True,include_instance_data=True)
        self.luisrec= LuisRecognizer(luisapp,luisoption,True)


    async def initial_step( self, step_context: WaterfallStepContext) -> DialogTurnResult:
        posa= await self.storage.read([str(step_context._turn_context.activity.from_property.id)]) #prendo le informazioni dell'utente dallo storage
        if len(posa) == 0:
            return await step_context.begin_dialog(RegDialog.__name__) #se non ho trovata alcuna informazione allora è un nuovo utente
        else:
            intent="aiuto"
            try:   
                result= await self.luisrec.recognize(step_context._turn_context) #utilizzo luis per capire l'intent dell'utente
                intent= LuisRecognizer.top_intent(result)
            except:
                intent="aiuto"
            if intent == "ricerca": #se l'intent è una ricerca ed ho riconosciuto il luogo passo il controllo a find dialog 
                if len(result.properties["luisResult"].entities) > 0:
                    lentity=result.properties["luisResult"].entities[0]
                    #idut=f"{step_context._turn_context.activity.from_property.id}"
                    #up=posa[idut]
                    #up.setcontents(lentity.entity)
                    #dicts={str(step_context._turn_context.activity.from_property.id): up}
                    #await self.storage.write(dicts)
                    return await step_context.begin_dialog(FindDialog.__name__,lentity.entity)
                else:
                   await step_context._turn_context.send_activity("Il luogo inserito non ha prodotto risultati, riprova")
                   return await step_context.end_dialog()
            elif intent == "cronologia": #se l'intent è cronologia avvio cronodialog
                return await step_context.begin_dialog(CronoDialog.__name__)
            elif intent == "aiuto": #se l'intent è aiuto avvio l'helpdialog
                return await step_context.begin_dialog(HelpDialog.__name__)
            else:
                return await step_context.begin_dialog(HelpDialog.__name__)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.end_dialog()
