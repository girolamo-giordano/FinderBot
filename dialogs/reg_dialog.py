from botbuilder.core import TurnContext,ActivityHandler,ConversationState,MessageFactory
from botbuilder.dialogs import DialogSet,WaterfallDialog,ComponentDialog,WaterfallStepContext
from botbuilder.dialogs.prompts import TextPrompt,PromptOptions
from botbuilder.azure import BlobStorage, BlobStorageSettings
from entity import UserProfile

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="var.env")
CONTAINER_NAME=os.getenv("BLOB_CONTAINER_NAME")
CONTAINER_STRING=os.getenv("BLOB_CONNECTION_STRING")

class RegDialog(ComponentDialog):
    def __init__(self, conversation:ConversationState):
        super(RegDialog, self).__init__(RegDialog.__name__ or None)
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(WaterfallDialog("main_dialog",[self.getName,self.completedProcess]))
        self.initial_dialog_id= "main_dialog"
        blob_settings = BlobStorageSettings(
            container_name=CONTAINER_NAME,
            connection_string=CONTAINER_STRING
        )
        self.storage = BlobStorage(blob_settings)

    
    async def getName(self,step_context:WaterfallStepContext):
        prompt_options = PromptOptions(
            prompt=MessageFactory.text("Benvenuto su FinderBot, inserisci il tuo nome per registrarti.")
        )
        return await step_context.prompt(TextPrompt.__name__, prompt_options)
    
    async def completedProcess(self, step_context:WaterfallStepContext):
        dicts={str(step_context._turn_context.activity.from_property.id): UserProfile(name=step_context.result, contents=[])}
        await self.storage.write(dicts)
        await step_context.context.send_activity(
            MessageFactory.text(f"Registrazione effettuata con successo, benvenuto {step_context.result}.\n\n Per ricercare attrazioni da visitare di un determinato luogo puoi utilizzare la frase:'Informazioni su **inserisci città**'")
        )
        return await step_context.end_dialog()
    
    



